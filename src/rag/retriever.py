"""
ChromaDB Retriever for Products and Brand Guidelines

Provides retrieval functions to fetch relevant context:
1. get_product_context() - Exact match lookup by slug
2. get_brand_context() - Semantic search on brand guidelines
"""

import os
from typing import Optional
from dotenv import load_dotenv

import chromadb

load_dotenv()


# =============================================================================
# CONFIGURATION
# =============================================================================

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


def get_chroma_client():
    """Get or create ChromaDB client with persistence."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client


# =============================================================================
# PRODUCT RETRIEVAL
# =============================================================================

def get_product_context(slug: str) -> Optional[dict]:
    """
    Exact match lookup from products collection by slug metadata filter.

    Args:
        slug: Product slug (e.g., "chatgpt-plus")

    Returns:
        Full product details dict or None if not found
    """
    client = get_chroma_client()

    try:
        collection = client.get_collection("products")

        # Query with metadata filter for exact slug match
        results = collection.query(
            query_texts=[slug],  # Query text (not actually used for metadata filter)
            n_results=1,
            where={"slug": slug}  # Exact metadata match
        )

        if results["documents"] and len(results["documents"][0]) > 0:
            # Return metadata (contains all product fields)
            return results["metadatas"][0][0]

        return None

    except Exception as e:
        print(f"⚠️ Error retrieving product context: {e}")
        return None


def search_products_similar(
    query: str,
    n_results: int = 3,
    category: Optional[str] = None
) -> list[dict]:
    """
    Semantic search for similar products (useful for product recommendations).

    Args:
        query: Search query (e.g., "AI assistant for coding")
        n_results: Number of results to return
        category: Optional category filter

    Returns:
        List of product metadata dicts
    """
    client = get_chroma_client()

    try:
        collection = client.get_collection("products")

        # Build where filter for category if provided
        where_filter = {"category": category} if category else None

        # Semantic search
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )

        if results["metadatas"]:
            return results["metadatas"][0]

        return []

    except Exception as e:
        print(f"⚠️ Error searching products: {e}")
        return []


# =============================================================================
# BRAND GUIDELINES RETRIEVAL
# =============================================================================

def get_brand_context(query: str, k: int = 3) -> str:
    """
    Semantic search on brand guidelines. Returns top-k relevant chunks
    concatenated as a single string.

    This becomes the brand context injected into every content generation prompt.

    Args:
        query: Search query describing what brand info is needed
                (e.g., "Facebook tone and formatting guidelines")
        k: Number of chunks to retrieve (default: 3)

    Returns:
        Concatenated brand guidelines text or empty string if error
    """
    client = get_chroma_client()

    try:
        collection = client.get_collection("brand")

        # Semantic search
        results = collection.query(
            query_texts=[query],
            n_results=k
        )

        if results["documents"] and len(results["documents"][0]) > 0:
            # Concatenate all chunks with section headers
            chunks = results["documents"][0]
            metadatas = results["metadatas"][0]

            context_parts = []
            for chunk, metadata in zip(chunks, metadatas):
                section_name = metadata.get("section_name", "Unknown Section")
                context_parts.append(f"## {section_name}\n{chunk}")

            return "\n\n---\n\n".join(context_parts)

        return ""

    except Exception as e:
        print(f"⚠️ Error retrieving brand context: {e}")
        return ""


def get_full_brand_guidelines() -> str:
    """
    Retrieve ALL brand guidelines (useful for system prompts).

    Returns:
        Full brand guidelines text concatenated
    """
    client = get_chroma_client()

    try:
        collection = client.get_collection("brand")

        # Get all documents
        results = collection.get()

        if results["documents"]:
            # Sort by chunk_index to maintain order
            documents = results["documents"]
            metadatas = results["metadatas"]

            # Sort by chunk_index
            sorted_docs = sorted(
                zip(documents, metadatas),
                key=lambda x: x[1].get("chunk_index", 0)
            )

            # Concatenate
            return "\n\n---\n\n".join([doc for doc, _ in sorted_docs])

        return ""

    except Exception as e:
        print(f"⚠️ Error retrieving full brand guidelines: {e}")
        return ""


# =============================================================================
# CONVENIENCE FUNCTIONS FOR AGENTS
# =============================================================================

def get_context_for_campaign(
    product_slug: str,
    brand_query: str = "platform-specific tone and formatting guidelines"
) -> tuple[Optional[dict], str]:
    """
    Get both product and brand context for a campaign.
    Convenience function for orchestrator and agents.

    Args:
        product_slug: Product slug to look up
        brand_query: Query for brand guidelines search

    Returns:
        Tuple of (product_info_dict, brand_context_string)
    """
    product_info = get_product_context(product_slug)
    brand_context = get_brand_context(brand_query, k=3)

    return product_info, brand_context


if __name__ == "__main__":
    # Test retrieval when run directly
    print("Testing ChromaDB retrieval...\n")

    # Test product lookup
    print("1. Testing product lookup:")
    product = get_product_context("chatgpt-plus")
    if product:
        print(f"   Found: {product['name']} - ৳{product['price_bdt']}/month")
    else:
        print("   Product not found")

    # Test brand context
    print("\n2. Testing brand context retrieval:")
    brand_ctx = get_brand_context("Facebook tone and hashtags", k=2)
    if brand_ctx:
        print(f"   Retrieved {len(brand_ctx)} characters of brand context")
        print(f"   Preview: {brand_ctx[:200]}...")
    else:
        print("   No brand context found")

    # Test similar products
    print("\n3. Testing similar products search:")
    similar = search_products_similar("AI assistant for developers", n_results=3)
    if similar:
        print(f"   Found {len(similar)} similar products:")
        for p in similar:
            print(f"   - {p['name']}")
    else:
        print("   No similar products found")
