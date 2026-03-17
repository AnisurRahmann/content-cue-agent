"""
Brands Service

Business logic for brand and product CRUD operations.
"""

from typing import List, Optional
from src.database import supabase
from src.brands.schemas import BrandCreate, BrandUpdate, ProductCreate, ProductUpdate


class BrandService:
    """Service for brand operations."""

    @staticmethod
    def get_brands(user_id: str) -> List[dict]:
        """Get all brands for a user."""
        response = supabase.table('brands').select('*').eq('user_id', user_id).execute()
        return response.data

    @staticmethod
    def get_brand(brand_id: str, user_id: str) -> Optional[dict]:
        """Get a specific brand by ID."""
        response = supabase.table('brands').select('*').eq('id', brand_id).eq('user_id', user_id).single()
        return response.data

    @staticmethod
    def create_brand(brand: BrandCreate, user_id: str) -> dict:
        """Create a new brand."""
        brand_data = brand.dict()
        brand_data['user_id'] = user_id

        response = supabase.table('brands').insert(brand_data).execute()
        return response.data[0]

    @staticmethod
    def update_brand(brand_id: str, brand: BrandUpdate, user_id: str) -> dict:
        """Update an existing brand."""
        brand_data = {k: v for k, v in brand.dict().items() if v is not None}

        response = supabase.table('brands').update(brand_data).eq('id', brand_id).eq('user_id', user_id).execute()
        return response.data[0]

    @staticmethod
    def delete_brand(brand_id: str, user_id: str) -> bool:
        """Delete a brand."""
        response = supabase.table('brands').delete().eq('id', brand_id).eq('user_id', user_id).execute()
        return len(response.data) > 0

    @staticmethod
    def get_products(brand_id: str, user_id: str) -> List[dict]:
        """Get all products for a brand."""
        # Verify user owns the brand
        brand = supabase.table('brands').select('id').eq('id', brand_id).eq('user_id', user_id).single()
        if not brand.data:
            return []

        response = supabase.table('products').select('*').eq('brand_id', brand_id).execute()
        return response.data

    @staticmethod
    def create_product(product: ProductCreate, brand_id: str, user_id: str) -> dict:
        """Create a new product for a brand."""
        # Verify user owns the brand
        brand = supabase.table('brands').select('id').eq('id', brand_id).eq('user_id', user_id).single()
        if not brand.data:
            raise ValueError("Brand not found or access denied")

        product_data = product.dict()
        product_data['brand_id'] = brand_id

        response = supabase.table('products').insert(product_data).execute()
        return response.data[0]

    @staticmethod
    def update_product(product_id: str, product: ProductUpdate, user_id: str) -> dict:
        """Update an existing product."""
        product_data = {k: v for k, v in product.dict().items() if v is not None}

        # Update product (RLS will verify user owns the brand)
        response = supabase.table('products').update(product_data).eq('id', product_id).execute()
        return response.data[0]

    @staticmethod
    def delete_product(product_id: str, user_id: str) -> bool:
        """Delete a product."""
        response = supabase.table('products').delete().eq('id', product_id).execute()
        return len(response.data) > 0
