import streamlit as st
import pandas as pd
import anthropic
import plotly.express as px
from datetime import datetime

# Setup page config
st.set_page_config(page_title="Quote Analysis Assistant", layout="wide")

# Initialize Anthropic client
def init_client():
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    return anthropic.Client(api_key=api_key)

def analyze_quotes(df, client):
    # Prepare the analysis prompt
    quote_details = df.to_string()
    
    prompt = f"""Analyze these contractor quotes and provide:
    1. Recommended contractor for award with reasoning
    2. Key negotiation points for each contractor
    3. Cost breakdown analysis
    4. Risk factors to consider

    Quote details:
    {quote_details}

    Format your response as a JSON with these keys:
    - recommended_contractor
    - recommendation_reasoning
    - negotiation_points (dict with contractor names as keys)
    - cost_analysis
    - risks
    """
    
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return eval(message.content)  # Convert string response to dict

def main():
    st.title("📊 Contractor Quote Analysis Assistant")
    
    # File upload
    st.subheader("Upload Quote Data")
    uploaded_file = st.file_uploader("Upload your quote comparison (CSV format)", type="csv")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("Quote Data")
            st.dataframe(df)
            
            if st.button("Analyze Quotes"):
                with st.spinner("Analyzing quotes..."):
                    client = init_client()
                    analysis = analyze_quotes(df, client)
                    
                    # Display results in organized sections
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🏆 Recommendation")
                        st.write(f"**Recommended Contractor:** {analysis['recommended_contractor']}")
                        st.write("**Reasoning:**")
                        st.write(analysis['recommendation_reasoning'])
                        
                        st.subheader("⚠️ Risk Factors")
                        st.write(analysis['risks'])
                    
                    with col2:
                        st.subheader("💰 Cost Analysis")
                        st.write(analysis['cost_analysis'])
                        
                        # Create cost breakdown visualization
                        cost_df = df.melt(
                            id_vars=['Contractor name'],
                            value_vars=['Labor Cost', 'Material Cost'],
                            var_name='Cost Type',
                            value_name='Amount'
                        )
                        
                        fig = px.bar(
                            cost_df,
                            x='Contractor name',
                            y='Amount',
                            color='Cost Type',
                            title='Cost Breakdown by Contractor',
                            barmode='group'
                        )
                        st.plotly_chart(fig)
                    
                    st.subheader("🤝 Negotiation Points")
                    for contractor, points in analysis['negotiation_points'].items():
                        with st.expander(f"Negotiation Strategy: {contractor}"):
                            st.write(points)
                            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your CSV file has the correct format with columns: "
                    "Contractor name, Itemcode, Description, Spec, Labor Cost, Material Cost, Total Cost")

if __name__ == "__main__":
    main()
