"""
Streamlit Dashboard - Main App

Multi-page dashboard for campaign management.
"""

import streamlit as st

st.set_page_config(
    page_title="ContentCued Marketing Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("ContentCued 🎯")
st.sidebar.markdown("---")

st.sidebar.markdown("### Navigation")
st.sidebar.markdown("""
- 📝 **New Campaign** - Create a new campaign
- 👁️ **Review** - Review & approve content
- 📊 **History** - Past campaigns & costs
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("""
Multi-agent marketing campaign generation with tiered LLM routing.

**Features:**
- 🤖 6 specialized agents
- 💰 Cost-optimized LLM tiers
- 📱 Cross-platform content
- 🎨 AI image generation
""")

st.sidebar.markdown("---")
st.sidebar.mark(f"<small>v0.1.0</small>", unsafe_allow_html=True)

# Main page
st.title("ContentCued Marketing Agent")
st.markdown("### 🎯 AI-Powered Cross-Platform Campaign Generation")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Campaigns", "0")

with col2:
    st.metric("Content Pieces", "0")

with col3:
    st.metric("Est. Cost", "$0.00")

st.markdown("---")

st.markdown("""
#### Welcome to ContentCued! 👋

This dashboard helps you create, review, and manage marketing campaigns
powered by multi-agent AI.

**Getting Started:**

1. 📝 Navigate to **New Campaign** to create a campaign brief
2. 👁️ Review generated content in **Review**
3. 📊 View campaign history and costs in **History**

**System Architecture:**

- **Tier 1 (Free):** Groq Llama 3.3 70B - routing, classification
- **Tier 2 (Cheap):** DeepSeek V3 - content generation
- **Tier 3 (Quality):** Claude Sonnet 4 - final polish

**Agents:**
1. 🎯 Orchestrator - plans & coordinates
2. ✍️ Copy Agent - generates all platform copy
3. 🎨 Visual Agent - creates images
4. 🔧 Adapter Agent - formats content
5. ✓ Quality Agent - validates everything
6. 📝 Blog Agent - writes SEO posts
""")
