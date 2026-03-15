#!/usr/bin/env python3
"""
One-time script to index products and brand guidelines into ChromaDB.

Run this after setting up the project to initialize the vector database:
    python scripts/index_data.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.indexer import index_all_data


if __name__ == "__main__":
    print("🚀 ContentCued Data Indexer")
    print("=" * 50)
    print("\nThis script will index:")
    print("  • Products (data/products.json)")
    print("  • Brand Guidelines (data/brand_guidelines.md)")
    print("\nStarting...\n")

    try:
        index_all_data()
        print("\n✅ Indexing complete!")
        print("\nYou can now run campaigns with RAG-enabled context retrieval.")
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        sys.exit(1)
