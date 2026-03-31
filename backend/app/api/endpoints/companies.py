from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.company import (
    Company, CompanyCreate, CompanyUpdate,
    CompanyContact, CompanyContactCreate,
    Company as CompanySchema,
    CompanyContact as CompanyContactSchema,
)
from app.crud.company import get_companies , get_company_by_tax_id, get_company_by_id, get_contacts_by_company, create_contact, count_companies, sync_external_company, soft_delete_company, update_company_status
from app.api import deps

router = APIRouter()

# --- Company Endpoints ---

@router.get("/", response_model=List[Company])
def read_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
):
    """ ดึงรายชื่อบริษัททั้งหมด พร้อมระบบ Search และ Pagination """
    items = get_companies(
        db, skip=skip, limit=limit, is_active=is_active, search=search
    )
    total = count_companies(db, is_active=is_active)
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
def create_company(obj_in: CompanyCreate, db: Session = Depends(get_db)):
    """สร้างบริษัทใหม่ (ตรวจสอบ Tax ID ซ้ำ)"""
    db_company = get_company_by_tax_id(db, tax_id=obj_in.tax_id)
    if db_company:
        raise HTTPException(status_code=400, detail="Tax ID already registered")
    return create_company(db, obj_in=obj_in)

@router.get("/{company_id}", response_model=Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    """ ดึงรายละเอียดบริษัทรายตัว พร้อมรายชื่อผู้ติดต่อ (Nested) """
    db_company = get_company_by_id(db, company_id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลบริษัท")
    return db_company

@router.post("/sync", response_model=CompanySchema)
def sync_single_company(obj_in: CompanyCreate, db: Session = Depends(get_db)):
    """ อัปเดตหรือสร้างบริษัทใหม่ (ใช้ตอนรับ Webhook หรือกด Sync จาก TRCloud) """
    return sync_external_company(db, company_in=obj_in)

@router.patch("/{company_id}/status", response_model=CompanySchema)
def toggle_company_status(
    company_id: int,
    is_active: bool = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """ เปิดหรือปิดการใช้งานบริษัท """
    db_company = update_company_status(db, company_id=company_id, is_active=is_active)
    if not db_company:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลบริษัทที่ต้องการอัปเดต")
    return db_company

@router.delete("/{company_id}", response_model=CompanySchema)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """ ลบบริษัทออกจากระบบ (Soft Delete) """
    db_company = soft_delete_company(db, company_id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลบริษัท หรือถูกลบไปแล้ว")
    return db_company

@router.get("/{company_id}/contacts", response_model=List[CompanyContactSchema])
def read_company_contacts(
    company_id: int, 
    search: Optional[str] = None, # รับค่า ?search=... จาก URL
    db: Session = Depends(get_db)
):
    return get_contacts_by_company(db, company_id=company_id, search=search)

@router.post("/{company_id}/contacts", response_model=CompanyContact)
def create_company_contact(
    company_id: int, 
    obj_in: CompanyContactCreate, 
    db: Session = Depends(get_db)
):
    """เพิ่มผู้ติดต่อใหม่เข้าไปในบริษัท"""
    db_company = get_company_by_id(db, company_id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return create_contact(db, obj_in=obj_in, company_id=company_id)
