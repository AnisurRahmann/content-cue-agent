"""
Dashboard Page: New Campaign

Create and submit new campaign briefs.
"""

import streamlit as st

st.set_page_config(page_title="New Campaign", page_icon="📝")

st.title("📝 New Campaign")
st.markdown("Create a new marketing campaign brief.")

# Product selection
with st.form("campaign_form"):
    st.markdown("### Campaign Details")

    col1, col2 = st.columns(2)

    with col1:
        product = st.selectbox(
            "Product *",
            [
                "chatgpt-plus",
                "gemini-pro",
                "midjourney",
                "canva-pro",
                "capcut-pro",
                "grammarly-premium",
                "microsoft-365",
                "perplexity-pro",
                "cursor-pro",
                "adobe-creative-cloud",
            ],
            help="Select the product to promote"
        )

        audience = st.text_input(
            "Target Audience *",
            value="Developers and content creators",
            help="Who are you targeting?"
        )

    with col2:
        tone = st.selectbox(
            "Tone",
            ["casual", "professional", "exciting", "informative"],
            help="Brand voice for this campaign"
        )

        campaign_type = st.radio(
            "Campaign Type",
            ["deal_drop", "education", "social_proof", "trending"],
            help="What type of campaign?"
        )

    st.markdown("### Platforms")
    st.markdown("Select which platforms to generate content for:")

    col1, col2, col3 = st.columns(3)

    with col1:
        facebook = st.checkbox("Facebook", value=True)
        instagram = st.checkbox("Instagram", value=True)

    with col2:
        linkedin = st.checkbox("LinkedIn", value=True)
        whatsapp = st.checkbox("WhatsApp", value=True)

    with col3:
        blog = st.checkbox("Blog", value=False)

    platforms = []
    if facebook: platforms.append("facebook")
    if instagram: platforms.append("instagram")
    if linkedin: platforms.append("linkedin")
    if whatsapp: platforms.append("whatsapp")
    if blog: platforms.append("blog")

    st.markdown("### Special Instructions")
    instructions = st.text_area(
        "Additional instructions (optional)",
        placeholder="E.g., Focus on instant activation, mention local pricing...",
        help="Any specific requirements for this campaign"
    )

    submitted = st.form_submit_button("🚀 Generate Campaign", type="primary")

    if submitted:
        if not platforms:
            st.error("Please select at least one platform")
        else:
            st.success("Campaign brief created!")

            st.json({
                "product_slug": product,
                "audience": audience,
                "platforms": platforms,
                "tone": tone,
                "campaign_type": campaign_type,
                "instructions": instructions
            })

            st.info("💡 In production, this would trigger the workflow via the API")

# Display product info
st.markdown("---")
st.markdown("### Product Information")

product_info = {
    "chatgpt-plus": {"name": "ChatGPT Plus", "price": "৳2,500", "category": "AI Assistant"},
    "gemini-pro": {"name": "Google Gemini Pro", "price": "৳2,800", "category": "AI Assistant"},
    "midjourney": {"name": "Midjourney", "price": "৳3,000", "category": "Image Generation"},
    "canva-pro": {"name": "Canva Pro", "price": "৳1,800", "category": "Design Tools"},
    "capcut-pro": {"name": "CapCut Pro", "price": "৳1,500", "category": "Video Editing"},
    "grammarly-premium": {"name": "Grammarly Premium", "price": "৳2,200", "category": "Writing Tools"},
    "microsoft-365": {"name": "Microsoft 365", "price": "৳3,200", "category": "Productivity Suite"},
    "perplexity-pro": {"name": "Perplexity Pro", "price": "৳2,400", "category": "AI Research"},
    "cursor-pro": {"name": "Cursor Pro", "price": "৳2,600", "category": "Development Tools"},
    "adobe-creative-cloud": {"name": "Adobe Creative Cloud", "price": "৳5,500", "category": "Creative Suite"},
}

info = product_info.get(product, {})
if info:
    col1, col2, col3 = st.columns(3)
    col1.metric("Name", info["name"])
    col2.metric("Price", info["price"])
    col3.metric("Category", info["category"])
