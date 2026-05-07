# dashboard.py - Complete Streamlit dashboard for competitor analysis
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

# Sidebar for upload
with st.sidebar:
    st.header("📁 Add New Analysis")
    uploaded_file = st.file_uploader("Upload competitor analysis CSV", type=["csv"])
    
    if uploaded_file is not None:
        new_data = pd.read_csv(uploaded_file)
        # Save to session state
        if 'all_analyses' in st.session_state:
            st.session_state.all_analyses = pd.concat([st.session_state.all_analyses, new_data], ignore_index=True)
        else:
            st.session_state.all_analyses = new_data
        st.success(f"✅ Added {len(new_data)} analyses")
    
    st.divider()
    st.caption("Built for Bajaj Broking Innovation Team")

# Load data
if 'all_analyses' not in st.session_state:
    # Try to load existing data
    try:
        st.session_state.all_analyses = pd.read_csv('competitor_analyses.csv')
    except:
        st.session_state.all_analyses = pd.DataFrame()

df = st.session_state.all_analyses

# Main dashboard
if len(df) > 0:
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # ===== ROW 1: KPIs =====
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Companies Analyzed", df['competitor'].nunique())
    with col2:
        st.metric("📁 Total Analyses", len(df))
    with col3:
        st.metric("🕒 Last Analysis", df['timestamp'].max().strftime('%Y-%m-%d'))
    with col4:
        st.metric("🎯 Benchmarked", len(df[df['benchmark'].notna()]))
    
    st.divider()
    
    # ===== ROW 2: Competitor Selector =====
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_competitor = st.selectbox(
            "Select Competitor",
            options=['All'] + sorted(df['competitor'].unique().tolist())
        )
    
    # Filter data
    if selected_competitor != 'All':
        filtered_df = df[df['competitor'] == selected_competitor]
    else:
        filtered_df = df
    
    # ===== ROW 3: Analysis Timeline =====
    st.subheader("📈 Analysis Timeline")
    
    timeline_data = filtered_df.groupby(filtered_df['timestamp'].dt.date).size().reset_index(name='count')
    fig = px.line(timeline_data, x='timestamp', y='count', 
                  title='Analyses Over Time',
                  markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # ===== ROW 4: Competitor Comparison =====
    st.subheader("🏢 Competitor Comparison")
    
    # Prepare data for comparison
    comparison = df.groupby('competitor').size().reset_index(name='analyses_count')
    fig = px.bar(comparison, x='competitor', y='analyses_count',
                 title='Number of Analyses by Competitor',
                 color='analyses_count',
                 color_continuous_scale='Blues')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # ===== ROW 5: Detailed View =====
    st.subheader("📄 Detailed Analysis")
    
    # Let user select which analysis to view
    analysis_options = filtered_df.apply(
        lambda x: f"{x['competitor']} - {x['timestamp'].strftime('%Y-%m-%d %H:%M')}", 
        axis=1
    ).tolist()
    
    if analysis_options:
        selected = st.selectbox("Select analysis to view", analysis_options)
        selected_row = filtered_df.iloc[analysis_options.index(selected)]
        
        # Display in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💰 Financials", "📊 Revenue Model", "🎯 Strategy", 
            "🔍 Benchmark", "💡 Recommendations"
        ])
        
        with tab1:
            st.markdown(selected_row['financial_highlights'])
        with tab2:
            st.markdown(selected_row['revenue_model'])
        with tab3:
            st.markdown(selected_row['strategic_priorities'])
        with tab4:
            st.markdown(selected_row['benchmark'])
        with tab5:
            st.markdown(selected_row['recommendations'])

else:
    st.info("👈 Upload your first competitor analysis CSV using the sidebar to get started!")
    
    # Show how to use
    with st.expander("📖 How to use this dashboard"):
        st.markdown("""
        1. Run the competitor analysis in Google Colab
        2. Download the CSV file generated
        3. Upload it here using the sidebar on the left
        4. View and compare multiple competitors over time
        """)
