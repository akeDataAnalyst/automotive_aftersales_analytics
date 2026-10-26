import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Automotive After-Sales Hub",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist Header Layout
st.title("Automotive After-Sales Analytics Hub")
st.caption("Executive Decision-Support Platform | Dealership Operations & Customer Retention")

st.markdown("---")

# Load and display network overview directly
@st.cache_data
def load_branches():
    paths = ["../data/raw", "data/raw", "../../data/raw"]
    for p in paths:
        target = os.path.join(p, "dim_branches.parquet")
        if os.path.exists(target):
            return pd.read_parquet(target)
    return None

df_branches = load_branches()

if df_branches is not None:
    st.subheader("Dealership Network Locations")
    
    # Identify available bay column
    bay_col = "service_bays" if "service_bays" in df_branches.columns else [c for c in df_branches.columns if "bay" in c.lower()][0]
    
    # Key Summary Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Branches", len(df_branches))
    c2.metric("Total Service Bays", int(df_branches[bay_col].sum()))
    c3.metric("Emirates Covered", df_branches["emirate"].nunique())
    
    st.markdown("###")
    st.dataframe(
        df_branches,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Data files not detected. Please ensure `src/data_generator.py` has been run.")

st.markdown("---")
st.caption("Developed by Aklilu Abera | Data Analyst")