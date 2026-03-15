"""
Dashboard Page: Review Campaign

Review and approve/reject generated content pieces.
"""

import streamlit as st

st.set_page_config(page_title="Review Campaign", page_icon="👁️")

st.title("👁️ Review Campaign")
st.markdown("Review and approve generated content.")

# Campaign selection
col1, col2 = st.columns([2, 1])

with col1:
    campaign_id = st.selectbox(
        "Select Campaign",
        ["campaign_001", "campaign_002", "campaign_003"],
        help="Choose a campaign to review"
    )

with col2:
    status = st.selectbox("Status", ["In Review", "Approved", "Rejected"])

st.markdown("---")

# Quality score
st.markdown("### Quality Score")
quality_score = st.slider("Overall Quality", 0.0, 1.0, 0.85, 0.05)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Score", f"{quality_score:.2f}")
with col2:
    st.metric("Content Pieces", "5")
with col3:
    st.metric("Issues", "1" if quality_score < 0.8 else "0")

st.markdown("---")

# Content pieces
st.markdown("### Content Pieces")

# Example content piece
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("#### Facebook Post")
        st.markdown("**Status:** Draft")
        st.info("🔥 ChatGPT Plus পাচ্ছেন মাত্র ৳2,500-তে! 😱\n\nGPT-4 ব্যবহার করুন এখনই। ইনস্ট্যান্ট অ্যাক্টিভেশন! ⚡\n\nWhatsApp করুন: wa.me/8801XXXXXXXXX")
        st.markdown("**Hashtags:** #ContentCued #AI #Bangladesh #Tech")

    with col2:
        action = st.radio("Action", ["✅ Approve", "❌ Reject"])
        feedback = st.text_area("Feedback (if rejected)", "")

st.markdown("---")

# Batch actions
st.markdown("### Batch Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ Approve All", type="primary"):
        st.success("All pieces approved!")

with col2:
    if st.button("❌ Reject All"):
        st.warning("All pieces rejected")

with col3:
    if st.button("📤 Export"):
        st.info("Exporting campaign...")

st.markdown("---")

# Blog post section (if applicable)
st.markdown("### Blog Post")
with st.expander("View Blog Post"):
    st.markdown("#### Title: ChatGPT Plus in Bangladesh - Complete Guide")
    st.markdown("""
    **Introduction**

    Are you looking for ChatGPT Plus in Bangladesh? You're in the right place!
    In this guide, we'll cover everything you need to know about getting
    ChatGPT Plus with local pricing and instant activation.

    **What is ChatGPT Plus?**

    ChatGPT Plus is OpenAI's premium subscription that gives you access to:
    - GPT-4 and GPT-4o
    - Faster response times
    - Priority access during peak hours
    - Early access to new features

    **Pricing in Bangladesh**

    Get ChatGPT Plus for only ৳2,500/month with instant activation.
    No more complicated payment processes - simple bKash payment!
    """)

# Submit review
st.markdown("---")
if st.button("🚀 Submit Review", type="primary"):
    st.success("Review submitted! Campaign is being finalized...")
