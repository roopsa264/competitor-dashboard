import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Bajaj Broking - Competitor Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Bajaj Broking - Competitor Intelligence Dashboard")
st.markdown("*AI-powered analysis of investor presentations*")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Analysis")
    
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    
    if uploaded_file is not None:
        df_new = pd.read_csv(uploaded_file)
        st.session_state.df = df_new
        st.success(f"✅ Loaded {len(df_new)} competitor analyses")
        
        # Show what columns were found
        st.write("**Columns found:**")
        st.write(list(df_new.columns))
    
    st.divider()
    st.caption("Built for Bajaj Broking Innovation Team")

# Main content
df = st.session_state.df

if len(df) > 0:
    # Display basic info
    st.subheader("📊 Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 Competitors Analyzed", df['competitor'].nunique() if 'competitor' in df.columns else len(df))
    with col2:
        st.metric("📁 Total Analyses", len(df))
    with col3:
        if 'timestamp' in df.columns:
            latest = pd.to_datetime(df['timestamp']).max().strftime('%Y-%m-%d')
            st.metric("🕒 Latest Analysis", latest)
        else:
            st.metric("🕒 Latest Analysis", "Today")
    
    st.divider()
    
    # Select competitor to view
    if 'competitor' in df.columns:
        competitors = ['All'] + sorted(df['competitor'].unique().tolist())
        selected = st.selectbox("Select Competitor", competitors)
        
        if selected != 'All':
            filtered_df = df[df['competitor'] == selected]
        else:
            filtered_df = df
    else:
        filtered_df = df
        selected = "All"
    
    # Show analyses
    st.subheader("📄 Analysis Results")
    
    for idx, row in filtered_df.iterrows():
        with st.expander(f"📊 {row.get('competitor', row.get('filename', f'Analysis {idx+1}'))} - {row.get('timestamp', 'No date')[:10] if 'timestamp' in row else 'Recent'}"):
            
            # Show analysis text
            if 'analysis' in row and pd.notna(row['analysis']):
                st.markdown(row['analysis'])
            elif 'full_analysis' in row and pd.notna(row['full_analysis']):
                st.markdown(row['full_analysis'])
            else:
                st.warning("No analysis text found")
            
            # Show metadata
            st.caption(f"📁 File: {row.get('filename', 'Unknown')}")
            if 'status' in row:
                st.caption(f"✅ Status: {row['status']}")
    
    # Download button for combined data
    st.divider()
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download All Data as CSV",
        data=csv_data,
        file_name=f"competitor_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    # No data uploaded yet
    st.info("👈 **Upload your competitor analysis CSV** using the sidebar on the left")
    
    with st.expander("📖 How to use this dashboard"):
        st.markdown("""
        1. Run the competitor analysis in **Google Colab**
        2. Download the CSV file that gets generated
        3. Upload it here using the **sidebar uploader**
        4. View all competitor insights in one place
        
        **Expected CSV columns:**
        - `competitor` - Name of the broking firm
        - `timestamp` - When analysis was done  
        - `analysis` - Full AI analysis text
        - `filename` - Original file name
        """)
    
    # Show example
    st.subheader("📋 Example of what you'll see:")
    st.code("""
    ## FINANCIAL HIGHLIGHTS
    - Revenue: ₹8,000 Cr
    - Profit: ₹4,000 Cr
    - Clients: 7 million
    
    ## ACTIONABLE RECOMMENDATIONS
    1. Launch AI-powered advisory
    2. Expand to tier-2 cities
    3. Introduce zero-brokerage F&O
    """)
