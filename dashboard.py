import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Competitor Analysis", layout="wide")

st.title("📊 Bajaj Broking - Competitor Analysis")
st.markdown("Upload your CSV file from Google Colab")

# File uploader
uploaded_file = st.file_uploader("Choose CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV
    df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ Loaded {len(df)} competitor analyses")
    
    # Show raw data first (to debug)
    with st.expander("📋 View Raw Data"):
        st.dataframe(df)
    
    st.divider()
    
    # Display each analysis
    for i, row in df.iterrows():
        # Get competitor name
        if 'competitor' in df.columns:
            name = row['competitor']
        else:
            name = row.get('filename', f'Competitor {i+1}')
        
        with st.expander(f"📊 {name}", expanded=True):
            # Show analysis text
            if 'analysis' in df.columns:
                st.markdown(row['analysis'])
            elif 'full_analysis' in df.columns:
                st.markdown(row['full_analysis'])
            else:
                st.warning("No analysis column found")
            
            # Show metadata
            st.caption(f"File: {row.get('filename', 'N/A')}")
            if 'timestamp' in df.columns:
                st.caption(f"Date: {row['timestamp'][:10]}")
            if 'status' in df.columns:
                st.caption(f"Status: {row['status']}")
    
    # Download button
    st.divider()
    csv = df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, f"data_{datetime.now().strftime('%Y%m%d')}.csv")

else:
    st.info("👈 Upload your CSV file from Google Colab")
    
    st.markdown("""
    ### How to get the CSV:
    1. Run the Colab notebook
    2. The CSV downloads automatically
    3. Upload it here using the button above
    
    ### What you'll see:
    - List of all competitors analyzed
    - Financial highlights
    - Revenue breakdown
    - Strategic insights
    - Recommendations for Bajaj Broking
    """)
