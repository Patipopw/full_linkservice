from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List
from datetime import date, datetime
from app.schemas.quotation_item import QuotationItem, QuotationItemCreate
from app.schemas.company import Company, CompanyContact 

class QuotationBase(BaseModel):
    quotation_no: Optional[str] = None 
    status: str = "draft"
    version: int = 0
    
    # Snapshot Fields: เก็บข้อมูล ณ วันที่ออกเอกสาร
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
    # --- เชื่อมโยงกับ Master Data ---
    company_id: int             # ID ของบริษัทในระบบ LinkService
    contact_id: Optional[int] = None # ID ของผู้ติดต่อในระบบ LinkService

    company_name: Optional[str] = None 
    customer_name: Optional[str] = None
    
    items: List[QuotationItemCreate] = []

class Quotation(QuotationBase):
    id: int
    quotation_no: str 
    
    # Foreign Keys
    company_id: int
    contact_id: Optional[int] = None
    
    # ข้อมูล Master Data ปัจจุบัน (Nested JSON)
    company: Optional[Company] = None
    contact_person: Optional[CompanyContact] = None
    
    items: List[QuotationItem] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class QuotationUpdate(BaseModel):
    company_name: Optional[str] = None
    customer_name: Optional[str] = None
    quotation_date: Optional[date] = None
    validity_date: Optional[date] = None
    sale_id: Optional[str] = None
    project_name: Optional[str] = None
    
    items: Optional[List[QuotationItemCreate]] = None 
    model_config = ConfigDict(from_attributes=True)

class QuotationStatusUpdate(BaseModel):
    status: str
