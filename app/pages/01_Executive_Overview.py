import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Executive Overview | UAE After-Sales",
    page_icon="",
    layout="wide"
)

st.markdown("## Executive Overview & Network Performance")
st.markdown("High-level executive scorecards tracking network revenue, repair order volumes, quality metrics, and regional performance across the UAE.")

# Data Loading with robust path resolution
@st.cache_data
def load_data():
    paths = ["../../data/raw", "data/raw", "../data/raw"]
    raw_dir = next((p for p in paths if os.path.exists(os.path.join(p, "fact_repair_orders.parquet"))), "data/raw")
    
    df_ro = pd.read_parquet(os.path.join(raw_dir, "fact_repair_orders.parquet"))
    df_branches = pd.read_parquet(os.path.join(raw_dir, "dim_branches.parquet"))
    df_bookings = pd.read_parquet(os.path.join(raw_dir, "fact_bookings.parquet"))
    return df_ro, df_branches, df_bookings

try:
    df_ro, df_branches, df_bookings = load_data()
    
    # Merge for analysis
    df_ro_merged = df_ro.merge(df_branches, on="branch_id", how="left")
    df_ro_merged["total_revenue"] = df_ro_merged["labor_revenue_aed"] + df_ro_merged["parts_revenue_aed"]
    
    # Executive KPI Metrics
    total_revenue = df_ro_merged["total_revenue"].sum()
    total_ros = len(df_ro_merged)
    avg_ro_rev = total_revenue / total_ros if total_ros > 0 else 0
    ftfr = (df_ro_merged["first_time_fix_flag"].sum() / total_ros) * 100
    
    # Display Top Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total After-Sales Revenue", f"AED {total_revenue:,.2f}")
    col2.metric("Total Completed ROs", f"{total_ros:,}")
    col3.metric("Avg Revenue per RO", f"AED {avg_ro_rev:,.2f}")
    col4.metric("First-Time Fix Rate (FTFR)", f"{ftfr:.1f}%")
    
    st.markdown("---")
    
    # Regional & Branch Revenue Breakdown
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Revenue by Branch Location")
        branch_rev = df_ro_merged.groupby("branch_name")["total_revenue"].sum().reset_index()
        branch_rev = branch_rev.sort_values(by="total_revenue", ascending=True)
        
        fig_branch = px.bar(
            branch_rev,
            x="total_revenue",
            y="branch_name",
            orientation="h",
            title="Gross Revenue by Branch (AED)",
            labels={"total_revenue": "Total Revenue (AED)", "branch_name": "Branch"},
            template="plotly_white"
        )
        st.plotly_chart(fig_branch, use_container_width=True)
        
    with col_r:
        st.subheader("Revenue Breakdown by Job Type")
        job_rev = df_ro_merged.groupby("job_type")["total_revenue"].sum().reset_index()
        
        fig_job = px.pie(
            job_rev,
            names="job_type",
            values="total_revenue",
            title="Revenue Share by Job Classification",
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig_job, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data. Please ensure `src/data_generator.py` has been executed successfully. Details: {e}")