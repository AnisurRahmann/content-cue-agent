"""
Brands Router

CRUD endpoints for brands and products.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from src.auth.dependencies import get_current_user_simple
from src.brands.schemas import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from src.brands.service import BrandService

router = APIRouter(prefix="/brands", tags=["brands"])


# ============================================================================
# BRANDS ENDPOINTS
# ============================================================================

@router.get("", response_model=List[BrandResponse])
async def get_brands(current_user: dict = Depends(get_current_user_simple)) -> List[dict]:
    """Get all brands for current user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    brands = BrandService.get_brands(current_user['id'])
    return brands


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: str, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Get a specific brand."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    brand = BrandService.get_brand(brand_id, current_user['id'])
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return brand


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand: BrandCreate, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Create a new brand."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        new_brand = BrandService.create_brand(brand, current_user['id'])
        return new_brand
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create brand: {str(e)}")


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(brand_id: str, brand: BrandUpdate, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Update an existing brand."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        updated_brand = BrandService.update_brand(brand_id, brand, current_user['id'])
        return updated_brand
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update brand: {str(e)}")


@router.delete("/{brand_id}")
async def delete_brand(brand_id: str, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Delete a brand."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    success = BrandService.delete_brand(brand_id, current_user['id'])
    if not success:
        raise HTTPException(status_code=404, detail="Brand not found")

    return {"message": "Brand deleted successfully"}


# ============================================================================
# PRODUCTS ENDPOINTS
# ============================================================================

@router.get("/{brand_id}/products", response_model=List[ProductResponse])
async def get_products(brand_id: str, current_user: dict = Depends(get_current_user_simple)) -> List[dict]:
    """Get all products for a brand."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    products = BrandService.get_products(brand_id, current_user['id'])
    return products


@router.post("/{brand_id}/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(brand_id: str, product: ProductCreate, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Create a new product for a brand."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        new_product = BrandService.create_product(product, brand_id, current_user['id'])
        return new_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create product: {str(e)}")


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product: ProductUpdate, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Update an existing product."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        updated_product = BrandService.update_product(product_id, product, current_user['id'])
        return updated_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update product: {str(e)}")


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user_simple)) -> dict:
    """Delete a product."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    success = BrandService.delete_product(product_id, current_user['id'])
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}
