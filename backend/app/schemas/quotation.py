from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List
from datetime import date, datetime
from app.schemas.quotation_item import QuotationItem, QuotationItemCreate

class QuotationBase(BaseModel):
    quotation_no: Optional[str] = None 
    status: str = "draft"
    version: int = 0
    company_name: str
    company_address: Optional[str] = None
    customer_name: str
    customer_tel: Optional[str] = None
    customer_email: Optional[str] = None
    quotation_date: date
    validity_date: date
    sale_name: str
    sale_email: Optional[str] = None
    total_amount: Decimal = Decimal("0.00")
    creator: Optional[str] = None
    creator_id: Optional[str] = None
    sale_id: str
    project_name: Optional[str] = None

class QuotationCreate(QuotationBase):
    # ยอมรับรายการสินค้าพร้อมกับตอนสร้างใบเสนอราคา
    items: List[QuotationItemCreate] = []

class Quotation(QuotationBase):
    id: int
    quotation_no: str 
    items: List[QuotationItem] = [] # ส่งรายการสินค้ากลับไปด้วยเมื่อดึงข้อมูล
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class QuotationUpdate(QuotationBase):
    # ทำให้ทุกฟิลด์จาก Base เป็น Optional ทั้งหมด
    company_name: Optional[str] = None
    customer_name: Optional[str] = None
    quotation_date: Optional[date] = None
    validity_date: Optional[date] = None
    sale_id: Optional[str] = None
    
    # เพิ่มส่วนของ Items หากต้องการอัปเดตรายการสินค้าไปพร้อมกัน
    # (แนะนำให้สร้าง Schema สำหรับ Update Item แยกต่างหากถ้า logic ซับซ้อน)
    items: Optional[List[QuotationItemCreate]] = None 

    class Config:
        from_attributes = True

class QuotationStatusUpdate(BaseModel):
    status: str