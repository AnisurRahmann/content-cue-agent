"""
Product Catalog Tool - LangChain tool wrapper for RAG product lookup.

This tool allows agents to query the product catalog via ChromaDB RAG.
"""

from typing import Optional
from langchain_core.tools import tool

from src.rag.retriever import get_product_context, search_products_similar


@tool
def get_product_info(product_slug: str) -> Optional[dict]:
    """
    Look up product information from the catalog by slug.

    Args:
        product_slug: The product slug (e.g., "chatgpt-plus", "midjourney")

    Returns:
        Product information dict with keys: name, category, price_bdt, description, features, etc.
        Returns None if product not found.

    Example:
        >>> get_product_info("chatgpt-plus")
        {
            "name": "ChatGPT Plus",
            "category": "AI Assistant",
            "price_bdt": 2500,
            "description": "...",
            "features": [...],
            ...
        }
    """
    return get_product_context(product_slug)


@tool
def search_products(query: str, category: Optional[str] = None, n_results: int = 3) -> list[dict]:
    """
    Search for products similar to a query using semantic search.

    Args:
        query: Natural language query describing what you're looking for
               (e.g., "AI assistant for coding", "image generation tool")
        category: Optional category filter (e.g., "AI Assistant", "Design Tools")
        n_results: Number of results to return (default: 3)

    Returns:
        List of product dicts matching the query

    Example:
        >>> search_products("AI assistant for developers")
        [
            {"name": "ChatGPT Plus", "price_bdt": 2500, ...},
            {"name": "Cursor Pro", "price_bdt": 2600, ...},
        ]
    """
    return search_products_similar(query, n_results=n_results, category=category)


if __name__ == "__main__":
    # Test the tools
    print("Testing Product Catalog Tools...\n")

    # Test exact lookup
    print("1. Exact Lookup (get_product_info):")
    result = get_product_info("chatgpt-plus")
    if result:
        print(f"   Found: {result['name']} - ৳{result['price_bdt']}/month")
    else:
        print("   Not found")

    # Test search
    print("\n2. Semantic Search (search_products):")
    results = search_products("AI assistant for developers")
    print(f"   Found {len(results)} results:")
    for r in results:
        print(f"   - {r['name']}: ৳{r['price_bdt']}/month")
