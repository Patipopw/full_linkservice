from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime

class CompanyContactBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    contact_id: Optional[int] = None

class CompanyContactCreate(CompanyContactBase):
    company_id: int

class CompanyContact(CompanyContactBase):
    id: int
    company_id: int
    model_config = ConfigDict(from_attributes=True)

class CompanyBase(BaseModel):
    name: str
    tax_id: str
    branch_code: str = "00000"
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    trcloud_id: Optional[str] = None
    code_number: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    is_active: bool = True
    last_synced_at: Optional[datetime] = None
    contacts: List[CompanyContact] = []
    model_config = ConfigDict(from_attributes=True)

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    tax_id: Optional[str] = None
    branch_code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    trcloud_id: Optional[str] = None
    code_number: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class CompanyContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    contact_id: Optional[int] = None # เลข ID จาก TRCloud

    model_config = ConfigDict(from_attributes=True)
