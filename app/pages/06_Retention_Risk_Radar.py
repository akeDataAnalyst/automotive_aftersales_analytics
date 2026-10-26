import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.express as px

st.set_page_config(
    page_title="Retention Risk Radar | UAE After-Sales",
    page_icon="",
    layout="wide"
)

st.markdown("## Retention Risk Radar & ML Churn Prediction")
st.markdown("Powered by Gradient Boosting Machine Learning to identify high-value customers at risk of defection and generate prioritized CRM outreach lists.")

# Data & Model Loading with robust path resolution
@st.cache_data
def load_risk_data():
    paths_proc = ["../../data/processed", "data/processed", "../data/processed"]
    paths_model = ["../../models", "models", "../models"]
    
    proc_dir = next((p for p in paths_proc if os.path.exists(os.path.join(p, "customer_lifecycle_segments.parquet"))), "data/processed")
    model_dir = next((p for p in paths_model if os.path.exists(os.path.join(p, "churn_gradient_boosting_model.pkl"))), "models")
    
    df_cust = pd.read_parquet(os.path.join(proc_dir, "customer_lifecycle_segments.parquet"))
    model = joblib.load(os.path.join(model_dir, "churn_gradient_boosting_model.pkl"))
    return df_cust, model

try:
    df_cust, model = load_risk_data()
    
    # Define features used during model training
    feature_cols = [
        "total_service_visits",
        "lifetime_spend_aed",
        "avg_declined_work_aed",
        "days_since_last_service",
        "crm_consent"
    ]
    
    # Predict probability of returning (Class 1). Churn probability = 1 - P(returning)
    X = df_cust[feature_cols]
    df_cust["prob_returning"] = model.predict_proba(X)[:, 1]
    df_cust["churn_risk_score"] = 1.0 - df_cust["prob_returning"]
    
    # Sidebar filters for risk threshold
    st.sidebar.markdown("### Churn Radar Controls")
    risk_threshold = st.sidebar.slider("Minimum Churn Risk Score", min_value=0.0, max_value=1.0, value=0.60, step=0.05)
    
    # Filter high risk customers
    high_risk_df = df_cust[df_cust["churn_risk_score"] >= risk_threshold].sort_values(by="lifetime_spend_aed", ascending=False)
    
    # High-level Metrics
    total_high_risk = len(high_risk_df)
    revenue_at_stake = high_risk_df["lifetime_spend_aed"].sum()
    avg_risk_score = high_risk_df["churn_risk_score"].mean() * 100 if total_high_risk > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("High-Risk Customers Flagged", f"{total_high_risk:,}")
    col2.metric("Total Lifetime Spend at Stake", f"AED {revenue_at_stake:,.2f}")
    col3.metric("Average Churn Risk Probability", f"{avg_risk_score:.1f}%")
    
    st.markdown("---")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Churn Risk Distribution Across Customer Base")
        fig_risk = px.histogram(
            df_cust,
            x="churn_risk_score",
            nbins=30,
            title="Distribution of Customer Defection Probabilities",
            labels={"churn_risk_score": "Churn Risk Score (0 = Low Risk, 1 = High Defection Risk)", "count": "Customer Count"},
            template="plotly_white",
            color_discrete_sequence=["#2563EB"]
        )
        fig_risk.add_vline(x=risk_threshold, line_dash="dash", line_color="red", annotation_text=f"Selected Threshold ({risk_threshold})")
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with col_r:
        st.subheader("Key Churn Drivers & Model Insights")
        st.markdown("""
        - **Days Since Last Service**: The strongest leading indicator of defection; customers crossing 365+ days without an RO show a steep drop in retention probability.
        - **Lifetime Spend**: High-value corporate & retail fleet owners require prioritized proactive service reminders.
        - **Declined Work Value**: Customers with unresolved or declined repair estimates are significantly more likely to abandon network service centers.
        """)
        
        st.info("**Actionable CRM Recommendation:** Export the filtered high-risk lead list below directly to the outbound WhatsApp/Call Center team for immediate service retention campaigns.")

    st.markdown("---")
    st.subheader("Actionable High-Risk Customer Outreach List")
    st.write(f"Showing customers with churn risk score $\\ge {risk_threshold}$ ordered by highest historical lifetime spend.")
    
    # Safely filter display columns present in dataset
    preferred_cols = [
        "customer_id", "customer_name", "first_name", "last_name", "phone", "mobile_number", 
        "emirate", "lifecycle_segment", "total_service_visits", "lifetime_spend_aed", 
        "days_since_last_service", "churn_risk_score", "crm_consent"
    ]
    display_cols = [c for c in preferred_cols if c in high_risk_df.columns]
    
    st.dataframe(
        high_risk_df[display_cols].style.format({
            "lifetime_spend_aed": "AED {:,.2f}",
            "churn_risk_score": "{:.2f}"
        }),
        use_container_width=True
    )
    
    # CSV Export for CRM team
    csv_data = high_risk_df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download High-Risk CRM Lead List (CSV)",
        data=csv_data,
        file_name="high_risk_retention_leads.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading churn model or risk data. Details: {e}")