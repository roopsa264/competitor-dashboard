# dashboard.py - Production Safe Fixed Version

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Bajaj Broking - Competitor Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("📊 Bajaj Broking - Competitor Intelligence Dashboard")
st.markdown("*AI-powered analysis of investor presentations from broking competitors*")

# =========================================================
# SESSION STATE INIT
# =========================================================

if 'all_analyses' not in st.session_state:
    st.session_state.all_analyses = pd.DataFrame()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📁 Add New Analysis")

    # -----------------------------------------------------
    # SINGLE FILE UPLOAD
    # -----------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload competitor analysis CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            new_data = pd.read_csv(uploaded_file)

            # Validate required columns
            required_cols = ['competitor']
            missing_cols = [c for c in required_cols if c not in new_data.columns]

            if missing_cols:
                st.error(f"❌ Missing required columns: {missing_cols}")
                st.stop()

            if len(new_data) > 0:

                combined = pd.concat(
                    [st.session_state.all_analyses, new_data],
                    ignore_index=True
                )

                # Remove duplicates
                st.session_state.all_analyses = combined.drop_duplicates()

                st.success(f"✅ Added {len(new_data)} analyses")
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error reading CSV: {e}")

    st.divider()

    # -----------------------------------------------------
    # BATCH UPLOAD
    # -----------------------------------------------------

    st.header("📦 Batch Upload")

    batch_files = st.file_uploader(
        "Upload multiple CSV files",
        type=["csv"],
        accept_multiple_files=True
    )

    if batch_files:

        all_batch_dfs = []

        for file in batch_files:

            try:
                df_batch = pd.read_csv(file)

                required_cols = ['competitor']
                missing_cols = [c for c in required_cols if c not in df_batch.columns]

                if missing_cols:
                    st.warning(
                        f"⚠️ {file.name} missing required columns: {missing_cols}"
                    )
                    continue

                all_batch_dfs.append(df_batch)

            except Exception as e:
                st.warning(f"⚠️ Could not read {file.name}: {e}")

        if all_batch_dfs:

            combined_batch = pd.concat(all_batch_dfs, ignore_index=True)

            combined = pd.concat(
                [st.session_state.all_analyses, combined_batch],
                ignore_index=True
            )

            # Remove duplicates
            st.session_state.all_analyses = combined.drop_duplicates()

            st.success(
                f"✅ Added {len(combined_batch)} analyses from {len(all_batch_dfs)} files"
            )

            st.rerun()

    st.divider()

    st.caption("Built for Bajaj Broking Innovation Team")

    # -----------------------------------------------------
    # DATA STATUS
    # -----------------------------------------------------

    if len(st.session_state.all_analyses) > 0:

        competitor_count = (
            st.session_state.all_analyses['competitor'].nunique()
            if 'competitor' in st.session_state.all_analyses.columns
            else 0
        )

        st.info(
            f"📊 Database contains "
            f"{len(st.session_state.all_analyses)} analysis records "
            f"from {competitor_count} competitors"
        )

# =========================================================
# LOAD DATA
# =========================================================

df = st.session_state.all_analyses.copy()

# =========================================================
# MAIN DASHBOARD
# =========================================================

if len(df) > 0 and 'competitor' in df.columns:

    # -----------------------------------------------------
    # TIMESTAMP CLEANING
    # -----------------------------------------------------

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(
            df['timestamp'],
            errors='coerce'
        )

    # =====================================================
    # KPI SECTION
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📊 Companies Analyzed",
            df['competitor'].nunique()
        )

    with col2:
        st.metric(
            "📁 Total Analyses",
            len(df)
        )

    with col3:

        if 'timestamp' in df.columns and df['timestamp'].notna().any():
            latest = df['timestamp'].max().strftime('%Y-%m-%d')
        else:
            latest = "N/A"

        st.metric(
            "🕒 Last Analysis",
            latest
        )

    with col4:

        benchmark_col = (
            'benchmark'
            if 'benchmark' in df.columns
            else 'benchmark_vs_bajaj'
        )

        if benchmark_col in df.columns:
            benchmarked = len(df[df[benchmark_col].notna()])
        else:
            benchmarked = 0

        st.metric(
            "🎯 Benchmarked",
            benchmarked
        )

    st.divider()

    # =====================================================
    # COMPETITOR FILTER
    # =====================================================

    col1, col2 = st.columns([1, 2])

    with col1:

        competitors_list = sorted(
            df['competitor'].dropna().unique().tolist()
        )

        selected_competitor = st.selectbox(
            "Select Competitor",
            options=['All'] + competitors_list
        )

    # Filter dataframe

    if selected_competitor != 'All':
        filtered_df = df[df['competitor'] == selected_competitor].copy()
    else:
        filtered_df = df.copy()

    filtered_df = filtered_df.reset_index(drop=True)

    # =====================================================
    # TIMELINE
    # =====================================================

    st.subheader("📈 Analysis Timeline")

    if 'timestamp' in filtered_df.columns:

        valid_timestamps = filtered_df[
            filtered_df['timestamp'].notna()
        ]

        if len(valid_timestamps) > 0:

            timeline_data = (
                valid_timestamps
                .groupby(valid_timestamps['timestamp'].dt.date)
                .size()
                .reset_index(name='count')
            )

            fig = px.line(
                timeline_data,
                x='timestamp',
                y='count',
                title='Analyses Over Time',
                markers=True
            )

            fig.update_layout(height=400)

            st.plotly_chart(
                fig,
                width='stretch'
            )

        else:
            st.info("No valid timestamps available.")

    else:
        st.info("Timestamp column not found.")

    # =====================================================
    # COMPETITOR COMPARISON
    # =====================================================

    st.subheader("🏢 Competitor Comparison")

    comparison = (
        df.groupby('competitor')
        .size()
        .reset_index(name='analyses_count')
    )

    if len(comparison) > 0:

        fig = px.bar(
            comparison,
            x='competitor',
            y='analyses_count',
            title='Number of Analyses by Competitor',
            color='analyses_count',
            color_continuous_scale='Blues'
        )

        fig.update_layout(height=400)

        st.plotly_chart(
            fig,
            width='stretch'
        )

    # =====================================================
    # DETAILED ANALYSIS
    # =====================================================

    st.subheader("📄 Detailed Analysis")

    # Build analysis options

    if 'timestamp' in filtered_df.columns:

        analysis_options = filtered_df.apply(
            lambda x:
            f"{x['competitor']} - "
            f"{x['timestamp'].strftime('%Y-%m-%d %H:%M')}"
            if pd.notna(x['timestamp'])
            else f"{x['competitor']} - No Date",
            axis=1
        ).tolist()

    else:

        analysis_options = filtered_df.apply(
            lambda x:
            f"{x['competitor']} - "
            f"{x['filename']}"
            if 'filename' in filtered_df.columns
            else f"{x['competitor']} - Analysis",
            axis=1
        ).tolist()

    # -----------------------------------------------------
    # ANALYSIS VIEWER
    # -----------------------------------------------------

    if analysis_options:

        selected = st.selectbox(
            "Select analysis to view",
            analysis_options
        )

        selected_idx = analysis_options.index(selected)

        selected_row = filtered_df.loc[selected_idx]

        # -------------------------------------------------
        # FULL ANALYSIS
        # -------------------------------------------------

        with st.expander(
            "📊 Full Analysis Results",
            expanded=True
        ):

            if (
                'analysis' in selected_row
                and pd.notna(selected_row['analysis'])
            ):

                st.markdown(selected_row['analysis'])

            elif (
                'full_analysis' in selected_row
                and pd.notna(selected_row['full_analysis'])
            ):

                st.markdown(selected_row['full_analysis'])

            else:
                st.warning(
                    "No detailed analysis text found."
                )

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        st.subheader("💡 Key Recommendations")

        recommendation_text = None

        for col in [
            'recommendations',
            'actionable_recommendations',
            'recommendations_text'
        ]:

            if (
                col in selected_row
                and pd.notna(selected_row[col])
            ):

                recommendation_text = selected_row[col]
                break

        # Direct recommendation column found

        if recommendation_text:

            st.info(recommendation_text[:1000])

        # Try extracting from analysis text

        else:

            if (
                'analysis' in selected_row
                and pd.notna(selected_row['analysis'])
            ):

                analysis_text = selected_row['analysis']

                if (
                    'RECOMMENDATIONS' in analysis_text
                    or 'recommendations' in analysis_text.lower()
                ):

                    rec_match = re.search(
                        r'(?:RECOMMENDATIONS|Actionable Recommendations)[\s\S]*?(?=\n##|\Z)',
                        analysis_text,
                        re.I
                    )

                    if rec_match:
                        st.info(rec_match.group(0)[:1000])

                    else:
                        st.warning(
                            "Recommendations section not found."
                        )

                else:
                    st.warning(
                        "No recommendation data available."
                    )

# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.info(
        "👈 **No data yet!** Upload your first competitor "
        "analysis CSV using the sidebar."
    )

    with st.expander("📖 How to use this dashboard"):

        st.markdown("""
### Step-by-Step Guide

1. Run the competitor analysis in Google Colab
2. Download the generated CSV
3. Upload the CSV using the sidebar
4. View KPIs, charts, and analysis insights

---

### Recommended CSV Columns

| Column | Purpose |
|---|---|
| competitor | Name of broking firm |
| timestamp | Analysis timestamp |
| analysis | Full analysis text |
| recommendations | Action items |
| revenue_cr | Revenue metric |
| profit_cr | Profit metric |

---

### Need a Test File?

1. Run your Colab notebook
2. Generate a competitor analysis
3. Download the CSV
4. Upload it here
""")

    # Preview section

    st.subheader("📊 Dashboard Preview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "**📈 Analysis Timeline** "
            "- Track competitor analysis activity"
        )

    with col2:
        st.markdown(
            "**🏢 Competitor Comparison** "
            "- Compare brokerages side by side"
        )
