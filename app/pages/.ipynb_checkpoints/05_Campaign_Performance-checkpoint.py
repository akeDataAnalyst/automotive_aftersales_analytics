import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="CRM & Campaign ROI | UAE After-Sales",
    page_icon="",
    layout="wide"
)

st.markdown("## CRM & Outbound Campaign Performance")
st.markdown("Analyzing channel conversion efficiency (WhatsApp Broadcast, SMS, Call Center) and promotional campaign ROI to maximize workshop booking fill rates.")

# Data Loading with robust path resolution
@st.cache_data
def load_crm_data():
    paths = ["../../data/raw", "data/raw", "../data/raw"]
    raw_dir = next((p for p in paths if os.path.exists(os.path.join(p, "fact_crm.parquet"))), "data/raw")
    
    df_crm = pd.read_parquet(os.path.join(raw_dir, "fact_crm.parquet"))
    return df_crm

try:
    df_crm = load_crm_data()
    
    # High-level Campaign Metrics
    total_outreach = len(df_crm)
    total_responses = df_crm["response_flag"].sum()
    total_bookings = df_crm["booking_created_flag"].sum()
    
    response_rate = (total_responses / total_outreach) * 100 if total_outreach > 0 else 0
    conversion_rate = (total_bookings / total_outreach) * 100 if total_outreach > 0 else 0
    booking_yield_rate = (total_bookings / total_responses) * 100 if total_responses > 0 else 0
    
    # Metric Display Scorecards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Outbound Contacts", f"{total_outreach:,}")
    col2.metric("Customer Response Rate", f"{response_rate:.1f}%")
    col3.metric("Bookings Generated", f"{total_bookings:,}")
    col4.metric("Overall Campaign Conversion Rate", f"{conversion_rate:.1f}%")
    
    st.markdown("---")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Booking Conversion Rate by Outbound Channel")
        channel_perf = df_crm.groupby("outbound_channel").agg(
            total_sent=("interaction_id", "count"),
            responses=("response_flag", "sum"),
            bookings=("booking_created_flag", "sum")
        ).reset_index()
        
        channel_perf["conversion_rate_pct"] = (channel_perf["bookings"] / channel_perf["total_sent"]) * 100
        channel_perf = channel_perf.sort_values("conversion_rate_pct", ascending=False)
        
        fig_channel = px.bar(
            channel_perf,
            x="outbound_channel",
            y="conversion_rate_pct",
            title="Conversion Yield (% Booked) by Channel",
            text="conversion_rate_pct",
            template="plotly_white",
            color="outbound_channel"
        )
        fig_channel.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_channel.add_hline(y=12, line_dash="dash", line_color="green", annotation_text="Target Benchmark (12%)")
        st.plotly_chart(fig_channel, use_container_width=True)
        
    with col_r:
        st.subheader("Campaign Yield by Promotion Type")
        camp_perf = df_crm.groupby("campaign_name").agg(
            total_sent=("interaction_id", "count"),
            bookings=("booking_created_flag", "sum")
        ).reset_index()
        
        camp_perf["conversion_rate_pct"] = (camp_perf["bookings"] / camp_perf["total_sent"]) * 100
        camp_perf = camp_perf.sort_values("conversion_rate_pct", ascending=True)
        
        fig_camp = px.bar(
            camp_perf,
            x="conversion_rate_pct",
            y="campaign_name",
            orientation="h",
            title="Campaign Type Effectiveness (%)",
            text="conversion_rate_pct",
            template="plotly_white",
            color_discrete_sequence=["#2563EB"]
        )
        fig_camp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_camp, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Detailed Outbound Campaign Performance Summary")
    st.dataframe(
        channel_perf.style.format({
            "total_sent": "{:,}",
            "responses": "{:,}",
            "bookings": "{:,}",
            "conversion_rate_pct": "{:.2f}%"
        }),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Error loading CRM campaign data: {e}")