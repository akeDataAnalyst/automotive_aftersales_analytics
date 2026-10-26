import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Customer Retention & Lifecycle | UAE After-Sales",
    page_icon="",
    layout="wide"
)

st.markdown("## Customer Retention & Lifecycle Segmentation")
st.markdown("Tracking customer lifecycle cohorts from active warranty service to post-warranty defection risks and expired maintenance intervals across the UAE.")

# Data Loading with robust path resolution
@st.cache_data
def load_retention_data():
    paths = ["../../data/processed", "data/processed", "../data/processed"]
    proc_dir = next((p for p in paths if os.path.exists(os.path.join(p, "customer_lifecycle_segments.parquet"))), "data/processed")
    df_cust = pd.read_parquet(os.path.join(proc_dir, "customer_lifecycle_segments.parquet"))
    return df_cust

try:
    df_cust = load_retention_data()
    
    # Metrics summary
    total_cust = len(df_cust)
    active_cust = len(df_cust[df_cust["lifecycle_segment"].str.contains("Active")])
    retention_rate = (active_cust / total_cust) * 100 if total_cust > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customer Database", f"{total_cust:,}")
    col2.metric("Active Fleet (0-6m)", f"{active_cust:,}")
    col3.metric("12-Month Service Retention Rate", f"{retention_rate:.1f}%")
    
    st.markdown("---")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Customer Distribution Across Lifecycle Segments")
        segment_counts = df_cust["lifecycle_segment"].value_counts().reset_index()
        segment_counts.columns = ["Segment", "Customer Count"]
        
        fig_seg = px.bar(
            segment_counts,
            x="Segment",
            y="Customer Count",
            title="Customer Count by Lifecycle Stage",
            text="Customer Count",
            template="plotly_white",
            color="Segment"
        )
        fig_seg.update_layout(xaxis_tickangle=-20, showlegend=False)
        st.plotly_chart(fig_seg, use_container_width=True)
        
    with col_r:
        st.subheader("Average Lifetime Spend by Lifecycle Segment")
        spend_seg = df_cust.groupby("lifecycle_segment")["lifetime_spend_aed"].mean().reset_index()
        
        fig_spend = px.bar(
            spend_seg,
            x="lifecycle_segment",
            y="lifetime_spend_aed",
            title="Avg Lifetime Spend (AED) per Segment",
            text="lifetime_spend_aed",
            template="plotly_white",
            color="lifecycle_segment"
        )
        fig_spend.update_traces(texttemplate='AED %{text:,.0f}', textposition='outside')
        fig_spend.update_layout(xaxis_tickangle=-20, showlegend=False)
        st.plotly_chart(fig_spend, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Emirate-wise Customer Segment Breakdown")
    emirate_seg = pd.crosstab(df_cust["emirate"], df_cust["lifecycle_segment"]).reset_index()
    st.dataframe(emirate_seg, use_container_width=True)

except Exception as e:
    st.error(f"Error loading customer retention data. Please ensure Notebook 2 (`02_customer_segmentation.ipynb`) has been executed to generate processed datasets. Details: {e}")