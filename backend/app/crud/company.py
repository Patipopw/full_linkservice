from sqlalchemy.orm import Session
from app.models.company import Company, CompanyContact
from app.schemas.company import CompanyCreate, CompanyContactCreate
from sqlalchemy import or_, func
from typing import Optional
from datetime import datetime

def get_company_by_id(db: Session, company_id: int):
    """ ดึงข้อมูลบริษัทรายตัว (ที่ยังไม่ถูกลบ) """
    return db.query(Company).filter(
        Company.id == company_id, 
        Company.deleted_at == None
    ).first()

def get_company_by_tax_id(db: Session, tax_id: str):
    return db.query(Company).filter(Company.tax_id == tax_id).first()

def get_companies(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = None, 
    search: Optional[str] = None
):
    """ ดึงรายการบริษัททั้งหมด พร้อมระบบ Search และ Filter """
    query = db.query(Company).filter(Company.deleted_at == None)
    
    if is_active is not None:
        query = query.filter(Company.is_active == is_active)
        
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Company.name.ilike(search_filter),
                Company.tax_id.ilike(search_filter),
                Company.code_number.ilike(search_filter)
            )
        )
    
    return query.order_by(Company.created_at.desc()).offset(skip).limit(limit).all()

def count_companies(db: Session, is_active: Optional[bool] = None):
    """ นับจำนวนบริษัททั้งหมดเพื่อทำ Pagination """
    query = db.query(func.count(Company.id)).filter(Company.deleted_at == None)
    if is_active is not None:
        query = query.filter(Company.is_active == is_active)
    return query.scalar()

def create_company(db: Session, obj_in: CompanyCreate):
    db_obj = Company(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def sync_external_company(db: Session, company_in: CompanyCreate):
    """ 
    อัปเดตหรือสร้างบริษัท (Upsert) 
    ใช้สำหรับ Webhook หรือข้อมูลจาก TRCloud โดยเช็คจาก tax_id
    """
    db_obj = db.query(Company).filter(
        Company.tax_id == company_in.tax_id,
        Company.deleted_at == None
    ).first()

    if db_obj:
        # Update ข้อมูลเดิม
        update_data = company_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db_obj.last_synced_at = datetime.now()
    else:
        # Create ใหม่
        db_obj = Company(**company_in.model_dump())
        db_obj.last_synced_at = datetime.now()
        db.add(db_obj)

    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_company_status(db: Session, company_id: int, is_active: bool):
    """ เปิด/ปิด การใช้งานบริษัท """
    db_obj = get_company_by_id(db, company_id)
    if db_obj:
        db_obj.is_active = is_active
        db.commit()
        db.refresh(db_obj)
    return db_obj

def soft_delete_company(db: Session, company_id: int):
    """ ลบบริษัทแบบ Soft Delete """
    db_obj = get_company_by_id(db, company_id)
    if db_obj:
        db_obj.deleted_at = datetime.now()
        db.commit()
        db.refresh(db_obj)
    return db_obj

def get_contacts_by_company(db: Session, company_id: int, search: str = None):
    # 1. เริ่มต้น Query โดยกรองเฉพาะบริษัทที่ระบุ และตัวที่ยังไม่ถูกลบ
    query = db.query(CompanyContact).filter(
        CompanyContact.company_id == company_id,
        CompanyContact.deleted_at == None
    )
    
    # 2. ถ้ามีการส่งคำค้นหามา
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                CompanyContact.name.ilike(search_filter),     # ค้นหาชื่อ
                CompanyContact.email.ilike(search_filter),    # ค้นหาอีเมล
                CompanyContact.phone.ilike(search_filter),    # ค้นหาเบอร์โทร
                CompanyContact.position.ilike(search_filter)  # ค้นหาตำแหน่ง
            )
        )
    
    # 3. จัดเรียงตามชื่อและส่งผลลัพธ์กลับ
    return query.order_by(CompanyContact.name.asc()).all()


def create_company_contact(db: Session, obj_in: CompanyContactCreate, company_id: int):
    """ เพิ่มผู้ติดต่อใหม่ """
    db_obj = CompanyContact(
        **obj_in.model_dump(exclude={"company_id"}), 
        company_id=company_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_contact(db: Session, obj_in: CompanyContactCreate, company_id: int):
    db_obj = CompanyContact(
        **obj_in.model_dump(exclude={"company_id"}), 
        company_id=company_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return 