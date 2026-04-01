from sqlalchemy.orm import Session
from app.models.quotation import Quotation
from datetime import datetime
from sqlalchemy import or_, func
from app.models.quotation_item import QuotationItem
from app.schemas.quotation import QuotationCreate, QuotationUpdate
from app.models.audit_log import AuditLog
from app.models.quotation import QuotationStatus
from typing import Optional, List

from app.models.quotation_note import QuotationNote
from app.models.product import Product as ProductModel
from app.models.company import CompanyContact, Company
from app.schemas.quotation_note import QuotationNoteCreate
from app.models.quotation import QuotationAttachment
from app.models.quotation_item import QuotationItemImage
from fastapi import UploadFile, HTTPException
import os
import uuid
import shutil
from pathlib import Path
from app.core.config import settings


MAX_FILE_SIZE = 5 * 1024 * 1024

def generate_quotation_no(db: Session):
    # 1. สร้าง Prefix: QT + YYMMDD (เช่น QT240320)
    now = datetime.now()
    date_str = now.strftime("%y%m%d") # %y คือปี 2 หลัก (24), %m เดือน (03), %d วัน (20)
    prefix = f"QT{date_str}"
    
    # 2. นับว่าวันนี้มีไปแล้วกี่ใบ (เช็คเฉพาะที่ขึ้นต้นด้วย Prefix ของวันนี้)
    count = db.query(func.count(Quotation.id)).filter(
        Quotation.quotation_no.like(f"{prefix}%")
    ).scalar()
    
    # 3. รันเลขต่อท้าย 4 หลัก (XXXX)
    next_number = (count or 0) + 1
    return f"{prefix}{next_number:04d}"

def create_quotation(db: Session, obj_in: QuotationCreate, creator_user: any):
    # 1. แยกข้อมูล Header
    quotation_data = obj_in.model_dump(exclude={"items", "quotation_no", "creator", "creator_id", "version"})
    
    # --- LOGIC: Auto-fill จาก Company Master ---
    if obj_in.company_id:
        company = db.query(Company).filter(Company.id == obj_in.company_id).first()
        if not company:
            raise HTTPException(status_code=400, detail="Company not found")
        
        quotation_data["company_name"] = quotation_data.get("company_name") or company.name
        quotation_data["company_address"] = quotation_data.get("company_address") or company.address
    else:
        # กรณีไม่มี company_id ต้องมั่นใจว่าส่ง company_name มา (ถ้า DB บังคับ)
        if not quotation_data.get("company_name"):
            raise HTTPException(status_code=400, detail="Company name is required if company_id is not provided")

    # 2. จัดการ Contact (Auto-fill หรือ Validate)
    if obj_in.contact_id:
        contact = db.query(CompanyContact).filter(CompanyContact.id == obj_in.contact_id).first()
        if not contact:
            raise HTTPException(status_code=400, detail="Contact person not found")
        
        quotation_data["customer_name"] = quotation_data.get("customer_name") or contact.name
        quotation_data["customer_tel"] = quotation_data.get("customer_tel") or contact.phone
        quotation_data["customer_email"] = quotation_data.get("customer_email") or contact.email


    new_no = generate_quotation_no(db)
    current_version = getattr(obj_in, "version", 0)

    # 2. สร้าง Header (Quotation)
    db_quotation = Quotation(
        **quotation_data,
        quotation_no=new_no,
        version=current_version,      
        creator=creator_user.full_name or creator_user.email, 
        creator_id=str(creator_user.id)
    )
    db.add(db_quotation)
    db.flush() 

    # 3. สร้างรายการสินค้า (Items) พร้อม Auto-fill จาก Product Master
    for item_in in obj_in.items:
        item_data = item_in.model_dump()
        
        # --- LOGIC: Auto-fill จาก Product Master ---
        if item_data.get("product_id"):
            product = db.query(ProductModel).filter(
                ProductModel.id == item_data["product_id"],
                ProductModel.deleted_at == None
            ).first()
            
            if product:
                # ถ้า User ไม่ได้กรอกค่ามา (หรือส่งมาเป็น null/empty) ให้ใช้จาก Master
                item_data["product_name"] = item_data.get("product_name") or product.name
                item_data["product_description"] = item_data.get("product_description") or product.description
                item_data["price"] = item_data.get("price") or product.standard_price
                item_data["cost"] = item_data.get("cost") or product.cost
                item_data["unit"] = item_data.get("unit") or product.unit
                item_data["product_part"] = item_data.get("product_part") or product.sku

        # --- คำนวณราคารวม (Total Price) ---
        qty = item_data.get("quantity") or 1
        price = item_data.get("price") or 0
        discount = item_data.get("discount_item") or 0
        item_data["total_item_price"] = (qty * price) - discount

        db_item = QuotationItem(
            **item_data,
            quotation_id=db_quotation.id
        )
        db.add(db_item)

    # 4. บันทึก Audit Log
    db.add(AuditLog(
        target_type="quotation",
        target_id=db_quotation.id,
        document_no=db_quotation.quotation_no,
        action="CREATE",
        changes={"initial_status": db_quotation.status},
        changed_by=creator_user.full_name or creator_user.email,
        changed_by_id=str(creator_user.id)
    ))
    
    db.commit()
    db.refresh(db_quotation)
    return db_quotation

def get_quotation(db: Session, quotation_id: int):
    return db.query(Quotation).filter(
        Quotation.id == quotation_id,
        Quotation.deleted_at == None
    ).first()

def get_quotation_by_no(db: Session, quotation_no: str):
    # ดึงใบที่เลขที่ตรงกัน และเอา Version ที่สูงที่สุด (ล่าสุด) เท่านั้น
    return db.query(Quotation).filter(
        Quotation.quotation_no == quotation_no,
        Quotation.deleted_at == None
    ).order_by(Quotation.version.desc()).first()

def get_quotations(db: Session, skip: int = 0, limit: int = 100):
    """
    ดึงรายการใบเสนอราคาเฉพาะเวอร์ชันล่าสุดของแต่ละเลขที่ และยังไม่ถูกลบ
    """
    # 1. สร้าง Subquery เพื่อหาเลข Version ที่สูงที่สุดของแต่ละ quotation_no
    subquery = (
        db.query(
            Quotation.quotation_no,
            func.max(Quotation.version).label("max_version")
        )
        .filter(Quotation.deleted_at == None)
        .group_by(Quotation.quotation_no)
        .subquery()
    )

    # 2. Join กลับมาที่ตารางหลักเพื่อดึงข้อมูลตัวเต็มของเวอร์ชันนั้นๆ
    query = (
        db.query(Quotation)
        .join(
            subquery,
            (Quotation.quotation_no == subquery.c.quotation_no) & 
            (Quotation.version == subquery.c.max_version)
        )
        .filter(Quotation.deleted_at == None)
        .order_by(Quotation.created_at.desc()) # เรียงตามวันที่สร้างล่าสุด
    )

    return query.offset(skip).limit(limit).all()

def get_quotation_history(db: Session, quotation_id: int):
    """
    ดึงประวัติการแก้ไข (Audit Logs) ทั้งหมดของ Quotation ใบนี้
    """
    return db.query(AuditLog).filter(
        AuditLog.target_type == "quotation",
        AuditLog.target_id == quotation_id
    ).order_by(AuditLog.created_at.desc()).all()

def get_quotation_revisions(db: Session, quotation_no: str):
    """
    ดึงรายการ Version ทั้งหมดของเลขที่ใบเสนอราคานี้
    """
    return db.query(Quotation).filter(
        Quotation.quotation_no == quotation_no,
        Quotation.deleted_at == None
    ).order_by(Quotation.version.desc()).all()

def search_quotations(
    db: Session, 
    query_str: str = None, 
    status: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
):
    """
    ค้นหาใบเสนอราคาเฉพาะ Latest Version โดยรองรับ Search String และ Status Filter
    """
    # 1. Subquery หา Latest Version (ใช้ Index: quotation_no, version, deleted_at)
    subquery = (
        db.query(
            Quotation.quotation_no,
            func.max(Quotation.version).label("max_version")
        )
        .filter(Quotation.deleted_at == None)
        .group_by(Quotation.quotation_no)
        .subquery()
    )

    # 2. Main Query Join กับ Subquery
    query = (
        db.query(Quotation)
        .join(
            subquery,
            (Quotation.quotation_no == subquery.c.quotation_no) & 
            (Quotation.version == subquery.c.max_version)
        )
        .filter(Quotation.deleted_at == None)
    )

    # 3. Apply Search Filter (ใช้ Index: quotation_no, company_name, customer_name)
    if query_str:
        search = f"%{query_str}%"
        query = query.filter(
            or_(
                Quotation.quotation_no.ilike(search),
                Quotation.company_name.ilike(search),
                Quotation.customer_name.ilike(search),
                Quotation.project_name.ilike(search)
            )
        )

    # 4. Apply Status Filter (ใช้ Index: status)
    if status:
        query = query.filter(Quotation.status == status.lower())

    # 5. Sorting & Pagination (ใช้ Index: created_at)
    return query.order_by(Quotation.created_at.desc()).offset(skip).limit(limit).all()

def update_quotation(db: Session, db_obj: Quotation, obj_in: QuotationUpdate, user: any):
    # --- 1. ตรวจสอบสถานะก่อนแก้ไข ---
    protected_statuses = ["win", "lost", "cancel"]
    if db_obj.status.lower() in protected_statuses:
        raise Exception(f"Cannot update quotation in '{db_obj.status}' status.")

    # --- 2. เตรียมข้อมูลและคำนวณ Audit Log (Diff) ---
    update_data = obj_in.model_dump(exclude_unset=True)
    changes_log = {}
    
    # วนลูปเช็คเฉพาะฟิลด์ใน Header (ข้าม items ไปก่อน)
    for field, new_value in update_data.items():
        if field == "items":
            continue
        old_value = getattr(db_obj, field)
        if str(old_value) != str(new_value):
            changes_log[field] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(new_value)
            }

    # --- LOGIC: ถ้ามีการเปลี่ยน Company/Contact ให้ทำ Snapshot ใหม่ ---
    if "company_id" in update_data and update_data["company_id"] != db_obj.company_id:
        company = db.query(Company).get(update_data["company_id"])
        if company:
            update_data["company_name"] = company.name
            update_data["company_address"] = company.address
            
    if "contact_id" in update_data and update_data["contact_id"] != db_obj.contact_id:
        contact = db.query(CompanyContact).get(update_data["contact_id"])
        if contact:
            update_data["customer_name"] = contact.name
            update_data["customer_tel"] = contact.phone
            update_data["customer_email"] = contact.email

    # --- 3. จัดการ Items (ถ้ามีการส่งมา) ---
    if "items" in update_data:
        new_items_in = update_data.pop("items")
        
        # ลบรายการเก่าออก
        db.query(QuotationItem).filter(QuotationItem.quotation_id == db_obj.id).delete()
        
        new_total_amount = 0
        for item_in in new_items_in:
            item_dict = item_in.model_dump()
            item_total = (item_dict["quantity"] * item_dict["price"]) - item_dict.get("discount_item", 0)
            item_dict["total_item_price"] = item_total
            new_total_amount += item_total
            
            db_item = QuotationItem(**item_dict, quotation_id=db_obj.id)
            db.add(db_item)
        
        # ตรวจสอบว่ายอดรวมเปลี่ยนไหมเพื่อลง Log
        if float(db_obj.total_amount) != float(new_total_amount):
            changes_log["total_amount"] = {"old": str(db_obj.total_amount), "new": str(new_total_amount)}
            changes_log["items"] = {"action": "items_list_updated"} # ระบุว่ารายการสินค้ามีการแก้ไข
            
        db_obj.total_amount = new_total_amount

    # --- 4. บันทึก Audit Log (ถ้ามีความเปลี่ยนแปลง) ---
    if changes_log:
        new_log = AuditLog(
            target_type="quotation",
            target_id=db_obj.id,
            document_no=db_obj.quotation_no,
            action="UPDATE",
            changes=changes_log,
            changed_by=user.full_name or user.email,
            changed_by_id=str(user.id)
        )
        db.add(new_log)

    # --- 5. อัปเดตฟิลด์ใน Header และ Version ---
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    # db_obj.version += 1 # อัปเดตเลข Version
    db_obj.updated_at = datetime.now()

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_quotation_status(db: Session, db_obj: Quotation, new_status: str, user: any):
    old_status = db_obj.status
    new_status_clean = new_status.lower()

    # 1. ตรวจสอบว่าสถานะเปลี่ยนจริงหรือไม่ (ถ้าเหมือนเดิมไม่ต้องทำอะไร)
    if old_status == new_status_clean:
        return db_obj

    # 2. บันทึกประวัติการเปลี่ยนสถานะลงใน Audit Log
    changes = {
        "status": {
            "old": old_status,
            "new": new_status_clean
        }
    }
    
    audit_entry = AuditLog(
        target_type="quotation",
        target_id=db_obj.id,
        document_no=db_obj.quotation_no,
        action="UPDATE_STATUS", # แยก action ให้ชัดเจนจาก UPDATE ข้อมูลทั่วไป
        changes=changes,
        changed_by=user.full_name or user.email,
        changed_by_id=str(user.id)
    )
    db.add(audit_entry)

    # 3. อัปเดตสถานะที่ Quotation Header
    db_obj.status = new_status_clean
    db_obj.updated_at = datetime.now()
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_quotation_revision(db: Session, quotation_id: int, user: any):
    # 1. ดึงข้อมูลใบต้นฉบับ
    original = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not original:
        raise Exception("Original quotation not found")

    # --- Logic: เปลี่ยนสถานะใบเก่าให้เป็น SUPERSEDED ---
    # เราจะไม่ Archive ใบที่สถานะสิ้นสุดแล้วอย่าง WIN/LOST/CANCEL (ขึ้นอยู่กับ Business Logic)
    terminal_statuses = [QuotationStatus.WIN, QuotationStatus.LOST, QuotationStatus.CANCEL]
    
    if original.status not in terminal_statuses:
        # เก็บสถานะเดิมไว้เพื่อลง Log
        old_status_val = original.status 
        original.status = QuotationStatus.SUPERSEDED
        
        # บันทึก Log ในใบเก่า
        db.add(AuditLog(
            target_type="quotation",
            target_id=original.id,
            document_no=original.quotation_no,
            action="ARCHIVED_BY_REVISION",
            changes={"status": {"old": old_status_val, "new": QuotationStatus.SUPERSEDED}},
            changed_by=user.full_name or user.email,
            changed_by_id=str(user.id)
        ))

    # 2. หา Version ถัดไป
    max_version = db.query(func.max(Quotation.version)).filter(
        Quotation.quotation_no == original.quotation_no
    ).scalar()
    new_version = (max_version or 0) + 1

    # 3. เตรียมข้อมูล Header (ข้ามฟิลด์ที่ไม่ต้องการ)
    header_data = {
        column.name: getattr(original, column.name) 
        for column in original.__table__.columns 
        if column.name not in ['id', 'created_at', 'updated_at', 'version', 'deleted_at', 'status']
    }

    # 4. สร้างใบใหม่ (Revision)
    db_revision = Quotation(
        **header_data,
        version=new_version,
        status=QuotationStatus.DRAFT, # ใบใหม่เริ่มที่ DRAFT เสมอ
        creator=user.full_name or user.email,
        creator_id=str(user.id)
    )
    db.add(db_revision)
    db.flush()

    # 5. คัดลอก Items
    for item in original.items:
        item_data = {
            column.name: getattr(item, column.name) 
            for column in item.__table__.columns 
            if column.name not in ['id', 'quotation_id']
        }
        db.add(QuotationItem(**item_data, quotation_id=db_revision.id))

    # 6. บันทึก Log ในใบใหม่
    db.add(AuditLog(
        target_type="quotation",
        target_id=db_revision.id,
        document_no=db_revision.quotation_no,
        action="REVISED_FROM",
        changes={"from_id": original.id, "from_version": original.version},
        changed_by=user.full_name or user.email,
        changed_by_id=str(user.id)
    ))

    db.commit()
    db.refresh(db_revision)
    return db_revision


def soft_delete_quotation(db: Session, quotation_id: int, user: any):
    """
    ทำ Soft Delete โดยเซตค่า deleted_at และบันทึก Log
    """
    db_obj = db.query(Quotation).filter(
        Quotation.id == quotation_id, 
        Quotation.deleted_at == None
    ).first()
    
    if not db_obj:
        raise Exception("Quotation not found or already deleted")

    # 1. บันทึก Audit Log ก่อนลบ
    db.add(AuditLog(
        target_type="quotation",
        target_id=db_obj.id,
        document_no=db_obj.quotation_no,
        action="DELETE",
        changes={"info": "Soft deleted"},
        changed_by=user.full_name or user.email,
        changed_by_id=str(user.id)
    ))

    # 2. เซตค่าวันที่ลบ
    db_obj.deleted_at = datetime.now()
    
    db.add(db_obj)
    db.commit()
    return {"message": "Successfully deleted", "id": quotation_id}

def get_quotation_audit_logs(db: Session, quotation_id: int):
    """
    ดึงประวัติการแก้ไขทั้งหมดของ Quotation ID นั้นๆ
    """
    return db.query(AuditLog).filter(
        AuditLog.target_type == "quotation",
        AuditLog.target_id == quotation_id
    ).order_by(AuditLog.created_at.desc()).all()

def get_quotation_versions(db: Session, quotation_no: str):
    """
    ดึงรายการ Version ทั้งหมดของเลขที่ใบเสนอราคานี้ (v0, v1, v2, ...)
    """
    return db.query(Quotation).filter(
        Quotation.quotation_no == quotation_no,
        Quotation.deleted_at == None
    ).order_by(Quotation.version.desc()).all()

def crud_create_quotation_note(db: Session, quotation_id: int, note_in: QuotationNoteCreate, user: any):
    db_note = QuotationNote(
        quotation_id=quotation_id,
        note_text=note_in.note_text,
        created_by=user.full_name or user.email # บันทึกชื่อผู้เขียน ณ ขณะนั้น
    )
    db.add(db_note)
    
    # บันทึกเข้า Audit Log เพื่อให้ Timeline หลักรับรู้
    db.add(AuditLog(
        target_type="quotation",
        target_id=quotation_id,
        action="ADD_NOTE",
        changes={"note": note_in.note_text},
        changed_by=user.full_name or user.email,
        changed_by_id=str(user.id)
    ))
    
    db.commit()
    db.refresh(db_note)
    return db_note

def get_quotation_notes(db: Session, quotation_id: int):
    return db.query(QuotationNote)\
        .filter(QuotationNote.quotation_id == quotation_id)\
        .order_by(QuotationNote.created_at.desc())\
        .all()

UPLOAD_BASE_DIR = Path(settings.UPLOAD_ROOT_DIR) / "quotations"

def crud_upload_quotation_attachment(db: Session, quotation_id: int, file: UploadFile, username: str):
    # 1. จัดการเรื่องไฟล์บน Disk
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # ใช้ Path สัมพัทธ์สำหรับเก็บใน DB
    relative_path = f"{quotation_id}/{unique_filename}"
    
    # ตำแหน่งที่จะวางไฟล์จริงในเครื่อง
    target_dir = UPLOAD_BASE_DIR / str(quotation_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_dest = target_dir / unique_filename

    # บันทึกไฟล์
    content = file.file.read() 
    with file_dest.open("wb") as buffer:
        buffer.write(content)
    
    # รีเซ็ตตำแหน่งไฟล์ (เผื่อมีการใช้ file ต่อหลังจากนี้)
    file.file.seek(0)

    # 2. บันทึกข้อมูลลง Database
    db_attachment = QuotationAttachment(
        quotation_id=quotation_id,
        file_name=file.filename,
        file_path=relative_path, # เก็บแค่ 1/uuid.pdf
        file_type=file.content_type,
        file_size=len(content),
        uploaded_by=username
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    
    return db_attachment

def crud_delete_quotation_attachment(db: Session, attachment_id: int):
    # 1. ค้นหาข้อมูลใน DB ก่อน
    db_attachment = db.query(QuotationAttachment).filter(QuotationAttachment.id == attachment_id).first()
    
    if db_attachment:
        # 2. ลบข้อมูลออกจาก Database
        db_attachment.deleted_at = datetime.now()
        db.commit()
        return True
        
    return False

def get_quotation_attachments(db: Session, quotation_id: int):
    return db.query(QuotationAttachment).filter(
        QuotationAttachment.quotation_id == quotation_id
    ).all()

def get_attachment_by_id(db: Session, attachment_id: int):
    return db.query(QuotationAttachment).filter(
        QuotationAttachment.id == attachment_id,
        QuotationAttachment.deleted_at == None
    ).first()


def crud_upload_item_images(db: Session, item_id: int, files: List[UploadFile], username: str):
    new_images = []
    
    # 1. เตรียม Directory (แยกตาม item_id เพื่อความเป็นระเบียบและป้องกันชื่อซ้ำข้าม item)
    item_dir = UPLOAD_BASE_DIR / "items" / str(item_id)
    item_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        if file.size > MAX_FILE_SIZE:
            # คุณสามารถเลือกข้ามไฟล์นี้ หรือ raise HTTPException ก็ได้
            continue 
        # 2. ตรวจสอบนามสกุลไฟล์ (กรองเฉพาะรูปภาพเหมือนฟังก์ชันแรก)
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            continue # ข้ามไฟล์ที่ไม่ใช่รูปภาพ

        # 3. จัดการไฟล์บน Disk
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        # เก็บ Path สัมพัทธ์เริ่มจาก items/ เพื่อให้ StaticFiles หาเจอ
        relative_path = f"items/{item_id}/{unique_filename}"
        file_dest = item_dir / unique_filename

        # อ่านและบันทึกไฟล์
        content = file.file.read()
        with open(file_dest, "wb") as buffer:
            buffer.write(content)
        
        # รีเซ็ตตำแหน่งไฟล์ (เผื่อมีการใช้ file ต่อ)
        file.file.seek(0)

        # 4. บันทึกลง Database (ตาราง QuotationItemImage)
        db_image = QuotationItemImage(
            item_id=item_id,
            file_name=file.filename,
            file_path=relative_path,
            file_type=file.content_type,
            uploaded_by=username
        )
        db.add(db_image)
        new_images.append(db_image)

    # 5. Commit และ Refresh ข้อมูลทั้งหมด
    db.commit()
    for img in new_images:
        db.refresh(img)
    
    return new_images


def crud_soft_delete_item_image(db: Session, image_id: int):
    # 1. ค้นหาข้อมูลรูปภาพ (กรองเอาตัวที่ยังไม่เคยโดนลบ)
    db_image = db.query(QuotationItemImage).filter(
        QuotationItemImage.id == image_id,
        QuotationItemImage.deleted_at == None
    ).first()
    
    if db_image:
        # 2. บันทึกเวลาที่ลบ (Soft Delete)
        db_image.deleted_at = datetime.now()
        
        # หมายเหตุ: ไม่ต้องลบไฟล์จริงออกจาก Disk เพื่อให้สามารถกู้คืนได้
        
        db.commit()
        db.refresh(db_image)
        return db_image
        
    return None

def get_item_images(db: Session, item_id: int):
    return db.query(QuotationItemImage).filter(
        QuotationItemImage.item_id == item_id,
        QuotationItemImage.deleted_at == None  # ดึงเฉพาะรูปที่ยังไม่ถูกลบ
    ).all()

def get_item_with_active_images(db: Session, item_id: int):
    # ดึง Item ที่ยังไม่ถูกลบ
    item = db.query(QuotationItem).filter(
        QuotationItem.id == item_id,
        QuotationItem.deleted_at == None
    ).first()
    
    if item:
        # กรองเฉพาะรูปภาพที่ยังไม่ถูกลบ (Active Images)
        # วิธีนี้จะช่วยให้ข้อมูลใน item.images มีเฉพาะรูปที่ใช้งานอยู่
        item.images = [img for img in item.images if img.deleted_at is None]
        
    return item

def clone_quotation(db: Session, db_source: Quotation, user: any):
    # 1. ดึงข้อมูลจากต้นฉบับ (ลบฟิลด์ที่ไม่ต้องการคัดลอกออก)
    source_data = {
        c.name: getattr(db_source, c.name) 
        for c in db_source.__table__.columns 
        if c.name not in ["id", "quotation_no", "version", "created_at", "updated_at", "deleted_at", "status"]
    }
    
    # 2. รันเลขที่เอกสารใหม่ และตั้งค่าพื้นฐานใหม่
    new_no = generate_quotation_no(db) # ฟังก์ชันรันเลขที่ของโปรเจกต์คุณ
    
    db_clone = Quotation(
        **source_data,
        quotation_no=new_no,
        version=0,                 # เริ่มนับ Version 0 ใหม่
        status="draft",            # สถานะเริ่มต้นต้องเป็น Draft เสมอ
        creator=user.full_name or user.email,
        creator_id=str(user.id),
        created_at=datetime.now()
    )
    db.add(db_clone)
    db.flush() # เพื่อให้ได้ ID ของใบใหม่มาใช้ผูกกับ Items

    # 3. คัดลอกรายการสินค้า (Items)
    for item in db_source.items:
        item_data = {
            c.name: getattr(item, c.name) 
            for c in item.__table__.columns 
            if c.name not in ["id", "quotation_id"]
        }
        db_item = QuotationItem(**item_data, quotation_id=db_clone.id)
        db.add(db_item)

    # 4. บันทึก Audit Log เพื่อบอกว่าใบนี้ Copy มาจากใบไหน
    db.add(AuditLog(
        target_type="quotation",
        target_id=db_clone.id,
        document_no=db_clone.quotation_no,
        action="CLONE",
        changes={"source_quotation_no": db_source.quotation_no},
        changed_by=user.full_name or user.email,
        changed_by_id=str(user.id)
    ))

    db.commit()
    db.refresh(db_clone)
    return db_clone