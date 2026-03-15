"""
Brand Context Tool - LangChain tool wrapper for RAG brand guidelines lookup.

This tool allows agents to query brand guidelines via ChromaDB RAG.
"""

from typing import Optional
from langchain_core.tools import tool

from src.rag.retriever import get_brand_context, get_full_brand_guidelines


@tool
def get_brand_guidelines(query: str, k: int = 3) -> str:
    """
    Search brand guidelines for relevant information.

    Args:
        query: Natural language query describing what brand info you need
               (e.g., "Facebook tone and formatting", "hashtag usage", "Bangla/English mixing")
        k: Number of guideline chunks to retrieve (default: 3)

    Returns:
        Relevant brand guidelines text

    Example:
        >>> get_brand_guidelines("Facebook post formatting")
        "## Platform-Specific Requirements
        ### Facebook
        - Image Size: 1200x630 pixels for posts
        - Text Length: <300 characters optimal
        - Hashtags: 3-5 relevant hashtags
        ..."
    """
    return get_brand_context(query, k=k)


@tool
def get_full_brand_guide() -> str:
    """
    Get the complete brand guidelines document.

    Useful for system prompts that need comprehensive brand context.

    Returns:
        Full brand guidelines text concatenated from all chunks

    Example:
        >>> get_full_brand_guide()
        "## Brand Identity
        ContentCued is Bangladesh's premier AI subscription service provider...
        ..."
    """
    return get_full_brand_guidelines()


@tool
def get_platform_guidelines(platform: str) -> str:
    """
    Get platform-specific content guidelines.

    Args:
        platform: One of: facebook, instagram, linkedin, whatsapp

    Returns:
        Platform-specific guidelines including tone, format, hashtags, etc.

    Example:
        >>> get_platform_guidelines("facebook")
        "## Platform-Specific Requirements
        ### Facebook
        - **Language:** Bangla-heavy (60-70% Bangla, 30-40% English)
        - **Tone:** Casual, energetic, community-focused
        - **Character Limit:** <300 characters for posts
        - **Hashtags:** #ContentCued #AI #Bangladesh #Tech (3-5 hashtags)
        ..."
    """
    query = f"{platform} platform tone format hashtags character limits"
    return get_brand_context(query, k=2)


if __name__ == "__main__":
    # Test the tools
    print("Testing Brand Context Tools...\n")

    # Test specific query
    print("1. Specific Query (get_brand_guidelines):")
    result = get_brand_guidelines("Facebook tone and hashtags")
    print(f"   Retrieved {len(result)} characters")
    print(f"   Preview: {result[:150]}...\n")

    # Test platform guidelines
    print("2. Platform Guidelines (get_platform_guidelines):")
    result = get_platform_guidelines("instagram")
    print(f"   Retrieved {len(result)} characters")
    print(f"   Preview: {result[:150]}...\n")

    # Test full guidelines
    print("3. Full Guidelines (get_full_brand_guide):")
    result = get_full_brand_guide()
    print(f"   Retrieved {len(result)} characters total")
