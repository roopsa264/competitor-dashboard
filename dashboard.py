# dashboard.py - Fixed version
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Bajaj Broking - Competitor Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Bajaj Broking - Competitor Intelligence Dashboard")
st.markdown("*AI-powered analysis of investor presentations from broking competitors*")

# Initialize session state for data storage
if 'all_analyses' not in st.session_state:
    st.session_state.all_analyses = pd.DataFrame()

# Sidebar for upload
with st.sidebar:
    st.header("📁 Add New Analysis")
    
    # Single file upload
    uploaded_file = st.file_uploader("Upload competitor analysis CSV", type=["csv"])
    
    if uploaded_file is not None:
        new_data = pd.read_csv(uploaded_file)
        if len(new_data) > 0:
            if len(st.session_state.all_analyses) > 0:
                st.session_state.all_analyses = pd.concat([st.session_state.all_analyses, new_data], ignore_index=True)
            else:
                st.session_state.all_analyses = new_data
            st.success(f"✅ Added {len(new_data)} analyses")
            st.rerun()
    
    st.divider()
    
    # Batch upload option
    st.header("📦 Batch Upload")
    batch_files = st.file_uploader("Upload multiple CSV files", 
                                   type=["csv"],
                                   accept_multiple_files=True)
    
    if batch_files:
        all_batch_dfs = []
        for file in batch_files:
            df_batch = pd.read_csv(file)
            all_batch_dfs.append(df_batch)
        
        if all_batch_dfs:
            combined_batch = pd.concat(all_batch_dfs, ignore_index=True)
            if len(st.session_state.all_analyses) > 0:
                st.session_state.all_analyses = pd.concat([st.session_state.all_analyses, combined_batch], ignore_index=True)
            else:
                st.session_state.all_analyses = combined_batch
            st.success(f"✅ Added {len(combined_batch)} analyses from {len(batch_files)} files")
            st.rerun()
    
    st.divider()
    st.caption("Built for Bajaj Broking Innovation Team")
    
    # Show data status
    if len(st.session_state.all_analyses) > 0:
        st.info(f"📊 Database contains {len(st.session_state.all_analyses)} analysis records from {st.session_state.all_analyses['competitor'].nunique() if 'competitor' in st.session_state.all_analyses.columns else 0} competitors")

# Get the data
df = st.session_state.all_analyses

# Main dashboard - Check if we have data
if len(df) > 0 and 'competitor' in df.columns:
    
    # Make sure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # ===== ROW 1: KPIs =====
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Companies Analyzed", df['competitor'].nunique())
    with col2:
        st.metric("📁 Total Analyses", len(df))
    with col3:
        if 'timestamp' in df.columns:
            latest = df['timestamp'].max().strftime('%Y-%m-%d')
        else:
            latest = "N/A"
        st.metric("🕒 Last Analysis", latest)
    with col4:
        benchmark_col = 'benchmark' if 'benchmark' in df.columns else 'benchmark_vs_bajaj'
        if benchmark_col in df.columns:
            st.metric("🎯 Benchmarked", len(df[df[benchmark_col].notna()]))
        else:
            st.metric("🎯 Benchmarked", "Upload data")
    
    st.divider()
    
    # ===== ROW 2: Competitor Selector =====
    col1, col2 = st.columns([1, 2])
    with col1:
        competitors_list = sorted(df['competitor'].unique().tolist())
        selected_competitor = st.selectbox(
            "Select Competitor",
            options=['All'] + competitors_list
        )
    
    # Filter data
    if selected_competitor != 'All':
        filtered_df = df[df['competitor'] == selected_competitor]
    else:
        filtered_df = df
    
    # ===== ROW 3: Analysis Timeline =====
    st.subheader("📈 Analysis Timeline")
    
    if 'timestamp' in df.columns:
        timeline_data = filtered_df.groupby(filtered_df['timestamp'].dt.date).size().reset_index(name='count')
        if len(timeline_data) > 0:
            fig = px.line(timeline_data, x='timestamp', y='count', 
                          title='Analyses Over Time',
                          markers=True)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Timestamp data not available - upload analyses with timestamps")
    
    # ===== ROW 4: Competitor Comparison =====
    st.subheader("🏢 Competitor Comparison")
    
    # Prepare data for comparison
    comparison = df.groupby('competitor').size().reset_index(name='analyses_count')
    if len(comparison) > 0:
        fig = px.bar(comparison, x='competitor', y='analyses_count',
                     title='Number of Analyses by Competitor',
                     color='analyses_count',
                     color_continuous_scale='Blues')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== ROW 5: Detailed View =====
    st.subheader("📄 Detailed Analysis")
    
    # Let user select which analysis to view
    if 'timestamp' in df.columns:
        analysis_options = filtered_df.apply(
            lambda x: f"{x['competitor']} - {x['timestamp'].strftime('%Y-%m-%d %H:%M') if pd.notna(x['timestamp']) else 'No date'}", 
            axis=1
        ).tolist()
    else:
        analysis_options = filtered_df.apply(
            lambda x: f"{x['competitor']} - {x['filename'] if 'filename' in x else 'Analysis'}", 
            axis=1
        ).tolist()
    
    if analysis_options:
        selected = st.selectbox("Select analysis to view", analysis_options)
        selected_idx = analysis_options.index(selected)
        selected_row = filtered_df.iloc[selected_idx]
        
        # Display the analysis content
        with st.expander("📊 Full Analysis Results", expanded=True):
            if 'analysis' in selected_row and pd.notna(selected_row['analysis']):
                st.markdown(selected_row['analysis'])
            elif 'full_analysis' in selected_row and pd.notna(selected_row['full_analysis']):
                st.markdown(selected_row['full_analysis'])
            else:
                st.warning("No detailed analysis text found in this record")
        
        # Parse and show recommendations separately if available
        st.subheader("💡 Key Recommendations")
        
        # Look for recommendations in various possible column names
        recommendation_text = None
        for col in ['recommendations', 'actionable_recommendations', 'recommendations_text']:
            if col in selected_row and pd.notna(selected_row[col]):
                recommendation_text = selected_row[col]
                break
        
        if recommendation_text:
            st.info(recommendation_text[:1000])
        else:
            # Try to extract from full analysis
            if 'analysis' in selected_row and pd.notna(selected_row['analysis']):
                analysis_text = selected_row['analysis']
                if 'RECOMMENDATIONS' in analysis_text or 'recommendations' in analysis_text.lower():
                    # Simple extraction
                    import re
                    rec_match = re.search(r'(?:RECOMMENDATIONS|Actionable Recommendations)[\s\S]*?(?=\n##|\Z)', analysis_text, re.I)
                    if rec_match:
                        st.info(rec_match.group(0)[:1000])

else:
    # Show helpful message when no data exists
    st.info("👈 **No data yet!** Upload your first competitor analysis CSV using the sidebar on the left.")
    
    with st.expander("📖 How to use this dashboard"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Run the competitor analysis in Google Colab** (use the notebook we built)
        2. **Download the CSV file** that gets generated after analysis
        3. **Upload the CSV here** using the sidebar uploader on the left
        4. **View the dashboard** - you'll see KPIs, charts, and detailed analysis
        
        ### Sample CSV Structure:
        Your CSV should have columns like:
        - `competitor` - Name of the broking firm
        - `timestamp` - When the analysis was done
        - `analysis` - Full text analysis results
        - `revenue_cr`, `profit_cr` (optional - for charts)
        
        ### Need a Test File?
        If you haven't run the Colab analysis yet, go back to your Colab notebook and:
        1. Run the analysis on any public brokerage PPT
        2. Download the CSV after completing Cell 5B or Cell 7
        3. Upload it here
        """)
    
    # Show example of what the dashboard will look like
    st.subheader("📊 Dashboard Preview (Once you upload data)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📈 Analysis Timeline** - Track how often you analyze competitors")
    with col2:
        st.markdown("**🏢 Competitor Comparison** - Compare multiple firms side by side")
