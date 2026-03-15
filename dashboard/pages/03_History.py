"""
Dashboard Page: Campaign History

View past campaigns, performance, and cost breakdowns.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campaign History", page_icon="📊")

st.title("📊 Campaign History")
st.markdown("View past campaigns and performance metrics.")

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Campaigns", "12")

with col2:
    st.metric("Total Content", "48")

with col3:
    st.metric("Avg. Quality", "0.87")

with col4:
    st.metric("Total Cost", "$2.45")

st.markdown("---")

# Campaign list
st.markdown("### Past Campaigns")

# Sample data
campaigns_data = {
    "Campaign ID": ["campaign_012", "campaign_011", "campaign_010", "campaign_009"],
    "Product": ["ChatGPT Plus", "Midjourney", "Canva Pro", "Cursor Pro"],
    "Date": ["2025-01-15", "2025-01-14", "2025-01-13", "2025-01-12"],
    "Platforms": ["FB, IG, LI, WA", "FB, IG, LI", "FB, IG, WA", "FB, IG, LI"],
    "Status": ["Approved", "Approved", "Review", "Approved"],
    "Cost": ["$0.28", "$0.32", "$0.25", "$0.30"],
}

df = pd.DataFrame(campaigns_data)
st.dataframe(df, use_container_width=True)

st.markdown("---")

# Selected campaign details
st.markdown("### Campaign Details")

selected_campaign = st.selectbox(
    "View Details",
    campaigns_data["Campaign ID"]
)

if selected_campaign:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Content Pieces")
        st.markdown("""
        - Facebook Post: ✅
        - Instagram Post: ✅
        - LinkedIn Post: ✅
        - WhatsApp Broadcast: ✅
        - Ad Variant 1: ✅
        - Ad Variant 2: ✅
        - Ad Variant 3: ✅
        """)

    with col2:
        st.markdown("#### Cost Breakdown")
        cost_data = {
            "Tier": ["Tier 1 (Free)", "Tier 2 (Cheap)", "Tier 3 (Quality)"],
            "Calls": [15, 3, 0],
            "Cost": ["$0.00", "$0.28", "$0.00"],
        }
        st.dataframe(pd.DataFrame(cost_data), use_container_width=True)

st.markdown("---")

# Cost trends
st.markdown("### Cost Trends")

st.line_chart({
    "Campaign Cost": [0.25, 0.30, 0.28, 0.32, 0.25, 0.30],
    "Avg Cost": [0.28, 0.28, 0.28, 0.28, 0.28, 0.28],
})

st.markdown("---")

# Cost comparison
st.markdown("### Tiered Routing Savings")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("With Tiering", "$2.45")
    st.caption("Actual cost with tiered routing")

with col2:
    st.metric("All Tier 3", "~$15.00")
    st.caption("Est. cost if all Tier 3")

with col3:
    st.metric("Savings", "$12.55", "+84%")
    st.caption("Cost reduction from tiering")

st.markdown("---")

st.info("💡 The tiered model routing reduces costs by ~84% compared to using quality models for all tasks.")
