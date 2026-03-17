"""
Brands Schemas

Pydantic models for brand CRUD operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BrandBase(BaseModel):
    """Base brand schema."""
    name: str
    brand_type: str = Field(default="business", pattern="^(business|personal)$")
    description: Optional[str] = None
    industry: Optional[str] = None
    voice_tone: str = "casual"
    voice_description: Optional[str] = None
    languages: List[str] = Field(default=["en"])
    primary_language: str = "en"
    brand_colors: Optional[dict] = None
    logo_url: Optional[str] = None
    guidelines_text: Optional[str] = None
    target_audiences: Optional[dict] = None
    default_platforms: List[str] = Field(default=["facebook", "instagram", "linkedin"])
    whatsapp_number: Optional[str] = None
    website_url: Optional[str] = None


class BrandCreate(BrandBase):
    """Brand creation schema."""
    pass


class BrandUpdate(BrandBase):
    """Brand update schema."""
    pass


class BrandResponse(BrandBase):
    """Brand response schema."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================


class ProductBase(BaseModel):
    """Base product schema."""
    slug: str
    name: str
    category: Optional[str] = None
    price: Optional[float] = None
    price_currency: str = "BDT"
    original_price: Optional[float] = None
    original_currency: str = "USD"
    duration: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    target_audience: Optional[str] = None
    activation_steps: Optional[List[str]] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


class ProductUpdate(ProductBase):
    """Product update schema."""
    pass


class ProductResponse(ProductBase):
    """Product response schema."""
    id: str
    brand_id: str
    created_at: datetime

    class Config:
        from_attributes = True
