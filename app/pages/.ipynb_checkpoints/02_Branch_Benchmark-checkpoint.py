import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Branch Benchmark | UAE After-Sales",
    page_icon="",
    layout="wide"
)

st.markdown("## Branch Benchmark & Variance Analysis")
st.markdown("Side-by-side comparative analysis of dealership branches, tracking bay capacity, labor vs. parts revenue yields, and operational quality.")

# Data Loading with robust path resolution
@st.cache_data
def load_benchmark_data():
    paths = ["../../data/raw", "data/raw", "../data/raw"]
    raw_dir = next((p for p in paths if os.path.exists(os.path.join(p, "dim_branches.parquet"))), "data/raw")
    
    df_branches = pd.read_parquet(os.path.join(raw_dir, "dim_branches.parquet"))
    df_ro = pd.read_parquet(os.path.join(raw_dir, "fact_repair_orders.parquet"))
    df_tech = pd.read_parquet(os.path.join(raw_dir, "dim_technicians.parquet"))
    return df_branches, df_ro, df_tech

try:
    df_branches, df_ro, df_tech = load_benchmark_data()
    
    # Merge ROs with branches
    df_ro_merged = df_ro.merge(df_branches, on="branch_id", how="left")
    df_ro_merged["total_revenue"] = df_ro_merged["labor_revenue_aed"] + df_ro_merged["parts_revenue_aed"]
    
    # Aggregate by branch
    branch_summary = df_ro_merged.groupby(["branch_id", "branch_name", "emirate", "location_type", "service_bays"]).agg(
        total_ros=("ro_id", "count"),
        labor_revenue=("labor_revenue_aed", "sum"),
        parts_revenue=("parts_revenue_aed", "sum"),
        total_revenue=("total_revenue", "sum"),
        avg_ro_rev=("total_revenue", "mean"),
        ftfr_pct=("first_time_fix_flag", lambda x: (x.sum() / len(x)) * 100)
    ).reset_index()
    
    branch_summary["rev_per_bay"] = branch_summary["total_revenue"] / branch_summary["service_bays"]
    
    st.subheader("Comprehensive Branch Performance Scorecard")
    st.dataframe(
        branch_summary[["branch_name", "emirate", "location_type", "service_bays", "total_ros", "total_revenue", "rev_per_bay", "ftfr_pct"]]
        .style.format({
            "total_revenue": "AED {:,.2f}",
            "rev_per_bay": "AED {:,.2f}",
            "ftfr_pct": "{:.1f}%"
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue Yield per Service Bay (AED)")
        fig_bay = px.bar(
            branch_summary.sort_values("rev_per_bay", ascending=True),
            x="rev_per_bay",
            y="branch_name",
            orientation="h",
            title="Revenue Generated per Service Bay",
            labels={"rev_per_bay": "Revenue per Bay (AED)", "branch_name": "Branch"},
            template="plotly_white"
        )
        st.plotly_chart(fig_bay, use_container_width=True)
        
    with col2:
        st.subheader("First-Time Fix Rate (FTFR %) by Branch")
        fig_ftfr = px.bar(
            branch_summary.sort_values("ftfr_pct", ascending=True),
            x="ftfr_pct",
            y="branch_name",
            orientation="h",
            title="FTFR Benchmarking (Target >= 95%)",
            labels={"ftfr_pct": "First-Time Fix Rate (%)", "branch_name": "Branch"},
            template="plotly_white"
        )
        fig_ftfr.add_vline(x=95, line_dash="dash", line_color="red", annotation_text="Target (95%)")
        st.plotly_chart(fig_ftfr, use_container_width=True)

except Exception as e:
    st.error(f"Error loading benchmark data: {e}")