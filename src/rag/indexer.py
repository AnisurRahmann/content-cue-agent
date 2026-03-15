"""
ChromaDB Indexer for Products and Brand Guidelines

Indexes two data sources into ChromaDB:
1. Product Catalog (data/products.json) - "products" collection
2. Brand Guidelines (data/brand_guidelines.md) - "brand" collection
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

import chromadb
from chromadb.config import Settings

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
# PRODUCT INDEXING
# =============================================================================

def index_products(products_path: str = "data/products.json") -> None:
    """
    Index products from JSON into ChromaDB "products" collection.

    Each product is one document with:
    - Embedding: name + description + features + target_audience
    - Metadata: slug, price_bdt, category, name
    """
    client = get_chroma_client()

    # Delete existing collection if it exists
    try:
        client.delete_collection("products")
    except Exception:
        pass

    # Create new collection
    collection = client.get_or_create_collection(
        name="products",
        metadata={"description": "Product catalog for ContentCued"}
    )

    # Load products
    with open(products_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        products = data["products"]

    # Prepare documents for indexing
    documents = []
    metadatas = []
    ids = []

    for product in products:
        # Create searchable text from product fields
        searchable_text = f"""
        Product: {product['name']}
        Category: {product['category']}
        Description: {product['description']}
        Features: {', '.join(product['features'])}
        Target Audience: {product['target_audience']}
        Price: ৳{product['price_bdt']}/month ({product['duration']})
        """.strip()

        documents.append(searchable_text)
        metadatas.append({
            "slug": product["slug"],
            "name": product["name"],
            "price_bdt": product["price_bdt"],
            "price_usd": product["price_usd"],
            "category": product["category"],
        })
        ids.append(product["slug"])

    # Add to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Indexed {len(products)} products to ChromaDB 'products' collection")


# =============================================================================
# BRAND GUIDELINES INDEXING
# =============================================================================

def index_brand_guidelines(guidelines_path: str = "data/brand_guidelines.md") -> None:
    """
    Index brand guidelines MD into ChromaDB "brand" collection.

    Splits content into chunks (~500 tokens each) for better retrieval.
    Each chunk has metadata: section_name
    """
    client = get_chroma_client()

    # Delete existing collection if it exists
    try:
        client.delete_collection("brand")
    except Exception:
        pass

    # Create new collection
    collection = client.get_or_create_collection(
        name="brand",
        metadata={"description": "ContentCued brand guidelines"}
    )

    # Read brand guidelines
    with open(guidelines_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into chunks by sections (## headers)
    chunks = []
    chunk_headers = []

    lines = content.split("\n")
    current_chunk = []
    current_header = "Introduction"

    for line in lines:
        # Detect section headers
        if line.startswith("## "):
            # Save previous chunk
            if current_chunk:
                chunk_text = "\n".join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                    chunk_headers.append(current_header)
                current_chunk = []

            # Start new chunk
            current_header = line[3:].strip()
            current_chunk.append(line)
        else:
            current_chunk.append(line)

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()
        if chunk_text:
            chunks.append(chunk_text)
            chunk_headers.append(current_header)

    # Prepare for indexing
    documents = []
    metadatas = []
    ids = []

    for i, (chunk, header) in enumerate(zip(chunks, chunk_headers)):
        documents.append(chunk)
        metadatas.append({
            "section_name": header,
            "chunk_index": i,
        })
        ids.append(f"brand_chunk_{i}")

    # Add to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Indexed {len(chunks)} brand guideline chunks to ChromaDB 'brand' collection")


# =============================================================================
# MAIN INDEXING FUNCTION
# =============================================================================

def index_all_data(
    products_path: str = "data/products.json",
    guidelines_path: str = "data/brand_guidelines.md"
) -> None:
    """Index all data sources (products + brand guidelines)."""
    print("🔍 Starting ChromaDB indexing...\n")

    index_products(products_path)
    index_brand_guidelines(guidelines_path)

    print(f"\n✅ All data indexed successfully to: {CHROMA_PERSIST_DIR}")
    print(f"📊 Collections:")
    client = get_chroma_client()
    for collection_name in ["products", "brand"]:
        collection = client.get_collection(collection_name)
        count = collection.count()
        print(f"   - {collection_name}: {count} documents")


if __name__ == "__main__":
    # Run indexing when script is executed directly
    index_all_data()
