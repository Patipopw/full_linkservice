from pydantic import BaseModel, ConfigDict, computed_field
from decimal import Decimal
from typing import Optional
from datetime import datetime
from app.core.config import settings 

class QuotationItemBase(BaseModel):
    item_no: int
    product_name: Optional[str] = None
    product_part: Optional[str] = None
    product_description: str
    red_note: Optional[str] = None
    quantity: Decimal = Decimal("1.00")
    unit: Optional[str] = None
    rent_duration: Optional[str] = None
    rent_period: Optional[str] = None
    vendor: Optional[str] = None
    price: Decimal = Decimal("0.00")
    cost: Decimal = Decimal("0.00")
    discount_item: Decimal = Decimal("0.00")
    total_item_price: Decimal = Decimal("0.00")
    remark: Optional[str] = None

class QuotationItemCreate(QuotationItemBase):
    pass


class QuotationItemImageSchema(BaseModel):
    id: int
    item_id: int
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: datetime

    @computed_field
    @property
    def url(self) -> Optional[str]:
        if not self.file_path:
            return None
        # ในอนาคตควรดึง http://localhost:8000 จาก settings.BASE_URL
        # return f"http://localhost:8000/uploads/{self.file_path}"
        return f"{settings.BACKEND_HOST}/uploads/{self.file_path}"

    model_config = ConfigDict(from_attributes=True)

class QuotationItem(QuotationItemBase):
    id: int
    quotation_id: int
    # เปลี่ยนจาก image_path (รูปเดียว) เป็น images (หลายรูป)
    images: list[QuotationItemImageSchema] = [] 
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)