import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Workshop Efficiency | UAE After-Sales",
    page_icon="",
    layout="wide"
)

st.markdown("## Workshop Efficiency & Quality Control")
st.markdown("Monitoring technician productivity, flat-rate vs. actual clocked hours, bay turnaround performance, and comeback quality metrics across UAE service hubs.")

# Data Loading with robust path resolution
@st.cache_data
def load_workshop_data():
    paths_proc = ["../../data/processed", "data/processed", "../data/processed"]
    paths_raw = ["../../data/raw", "data/raw", "../data/raw"]
    
    proc_dir = next((p for p in paths_proc if os.path.exists(os.path.join(p, "technician_performance.parquet"))), None)
    raw_dir = next((p for p in paths_raw if os.path.exists(os.path.join(p, "fact_repair_orders.parquet"))), "data/raw")
    
    df_tech_perf = pd.read_parquet(os.path.join(proc_dir, "technician_performance.parquet")) if proc_dir else None
    df_ro = pd.read_parquet(os.path.join(raw_dir, "fact_repair_orders.parquet"))
    df_branches = pd.read_parquet(os.path.join(raw_dir, "dim_branches.parquet"))
    
    return df_tech_perf, df_ro, df_branches

try:
    df_tech_perf, df_ro, df_branches = load_workshop_data()
    
    # Merge RO with Branch
    df_ro_merged = df_ro.merge(df_branches, on="branch_id", how="left")
    
    # High-level Metrics
    total_sold_hrs = df_ro["sold_labor_hours"].sum()
    total_clocked_hrs = df_ro["actual_clocked_hours"].sum()
    overall_efficiency = (total_sold_hrs / total_clocked_hrs) * 100 if total_clocked_hrs > 0 else 0
    comeback_count = df_ro["comeback_flag"].sum()
    comeback_rate = (comeback_count / len(df_ro)) * 100 if len(df_ro) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Billed Flat-Rate Hours", f"{total_sold_hrs:,.1f} hrs")
    col2.metric("Total Clocked Hours", f"{total_clocked_hrs:,.1f} hrs")
    col3.metric("Overall Technician Efficiency", f"{overall_efficiency:.1f}%")
    col4.metric("Comeback Rate (Target < 3.5%)", f"{comeback_rate:.2f}%")
    
    st.markdown("---")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Efficiency Distribution by Skill Level")
        if df_tech_perf is not None:
            skill_eff = df_tech_perf.groupby("skill_level")["technician_efficiency_pct"].mean().reset_index()
            fig_skill = px.bar(
                skill_eff,
                x="skill_level",
                y="technician_efficiency_pct",
                title="Average Efficiency (%) by Skill Level",
                text="technician_efficiency_pct",
                template="plotly_white",
                color="skill_level"
            )
            fig_skill.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_skill.add_hline(y=115, line_dash="dash", line_color="green", annotation_text="Target (115%)")
            st.plotly_chart(fig_skill, use_container_width=True)
        else:
            st.warning("Technician performance parquet file not found in processed data.")
            
    with col_r:
        st.subheader("Comeback Rate (%) by Branch Location")
        branch_cb = df_ro_merged.groupby("branch_name").agg(
            total_ros=("ro_id", "count"),
            comebacks=("comeback_flag", "sum")
        ).reset_index()
        branch_cb["comeback_rate"] = (branch_cb["comebacks"] / branch_cb["total_ros"]) * 100
        branch_cb = branch_cb.sort_values(by="comeback_rate", ascending=False)
        
        fig_cb = px.bar(
            branch_cb,
            x="branch_name",
            y="comeback_rate",
            title="Comeback / Repeat Repair Rate by Branch",
            text="comeback_rate",
            template="plotly_white",
            color_discrete_sequence=["#EF4444"]
        )
        fig_cb.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_cb.add_hline(y=3.5, line_dash="dash", line_color="black", annotation_text="Threshold (3.5%)")
        fig_cb.update_layout(xaxis_tickangle=-20)
        st.plotly_chart(fig_cb, use_container_width=True)

    if df_tech_perf is not None:
        st.markdown("---")
        st.subheader("Top 10 Most Efficient Technicians Network-Wide")
        top_techs = df_tech_perf.sort_values(by="technician_efficiency_pct", ascending=False).head(10)
        st.dataframe(
            top_techs[["technician_id", "skill_level", "total_jobs", "total_sold_hours", "total_clocked_hours", "technician_efficiency_pct"]]
            .style.format({
                "total_sold_hours": "{:,.1f}",
                "total_clocked_hours": "{:,.1f}",
                "technician_efficiency_pct": "{:.1f}%"
            }),
            use_container_width=True
        )

except Exception as e:
    st.error(f"Error loading workshop data: {e}")