from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    standard_price: Decimal = Decimal("0.00")
    cost: Decimal = Decimal("0.00")
    unit: Optional[str] = None
    external_id: Optional[str] = None
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    standard_price: Optional[Decimal] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    last_synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
