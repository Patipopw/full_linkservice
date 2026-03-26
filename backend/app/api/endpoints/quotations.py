from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.schemas.quotation import Quotation, QuotationCreate, QuotationUpdate, QuotationStatusUpdate
from app.schemas.quotation_item import QuotationItem, QuotationItemImageSchema
from app.schemas.quotation_note import QuotationNote as QuotationNoteSchema, QuotationNoteCreate
from app.schemas.audit_log import AuditLogSchema
from app.schemas.quotation_attachment import QuotationAttachmentSchema
from app.crud.quotation import create_quotation as crud_create_quotation, update_quotation
from app.crud.quotation import get_quotation, get_quotations
from app.crud.quotation import create_quotation_revision as crud_revised
from app.crud.quotation import soft_delete_quotation
from app.crud.quotation import get_quotation_versions as crud_get_versions
from app.crud.quotation import update_quotation_status
from app.crud.quotation import crud_create_quotation_note, get_quotation_notes
from app.api.auth import get_current_user
from app.crud.quotation import get_quotation_audit_logs
from app.dependencies.auth import PermissionChecker 
from app.models.user import User
from app.crud.quotation import crud_upload_quotation_attachment, crud_delete_quotation_attachment, get_quotation_attachments, crud_upload_item_images, crud_soft_delete_item_image, get_attachment_by_id, MAX_FILE_SIZE, UPLOAD_BASE_DIR

router = APIRouter()

@router.post("/", response_model=Quotation, status_code=status.HTTP_201_CREATED)
def create_new_quotation(
    quotation_in: QuotationCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # ดึง User จาก Token
):
    """
    สร้างใบเสนอราคาใหม่พร้อมรายการสินค้า (Items) ในครั้งเดียว
    """
    try:
        return crud_create_quotation(db=db, obj_in=quotation_in, creator_user=current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create quotation: {str(e)}"
        )

@router.get("/{quotation_id}", response_model=Quotation)
def read_quotation(quotation_id: int, db: Session = Depends(get_db), current_user: User = Depends(PermissionChecker("view_quotation"))):
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if db_quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return db_quotation

@router.get("/", response_model=List[Quotation])
def read_quotations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(PermissionChecker("view_quotation"))):
    return get_quotations(db, skip=skip, limit=limit)

@router.put("/{quotation_id}", response_model=Quotation)
def update_quotation_api(
    quotation_id: int,
    quotation_in: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # เช็คสิทธิ์ (Owner Only)
    if db_quotation.creator_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized")

    return update_quotation(db=db, db_obj=db_quotation, obj_in=quotation_in, user=current_user)

@router.delete("/{quotation_id}", status_code=status.HTTP_200_OK)
def delete_quotation_api(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    ลบใบเสนอราคา (Soft Delete)
    """
    try:
        return soft_delete_quotation(db=db, quotation_id=quotation_id, user=current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{quotation_id}/status", response_model=Quotation)
def change_quotation_status(
    quotation_id: int,
    status_in: QuotationStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    # ตัวอย่าง Role-based Access Control (RBAC)
    # ถ้าสถานะเป็น 'approved' อาจจะอนุญาตเฉพาะ user ที่เป็น 'manager' หรือ 'admin'
    if status_in.status.lower() == "approved" and current_user.role != "manager":
        raise HTTPException(
            status_code=403, 
            detail="Only managers can approve quotations"
        )

    # ป้องกันการเปลี่ยนกลับจากสถานะที่สิ้นสุดแล้ว
    if db_quotation.status in ["void", "rejected"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot change status from {db_quotation.status}"
        )

    try:
        return update_quotation_status(db=db, db_obj=db_quotation, new_status=status_in.status, user=current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{quotation_id}/revised", response_model=Quotation)
def post_quotation_revision(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return crud_revised(db=db, quotation_id=quotation_id, user=current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Could not create revision: {str(e)}"
        )
    
@router.get("/{quotation_id}/history", response_model=List[AuditLogSchema])
def read_quotation_history(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    ดึง Timeline ประวัติการแก้ไข (Created, Updated, Status Changed, Deleted)
    """
    # 1. เช็คก่อนว่า Quotation นี้มีจริงไหม (และเรามีสิทธิ์ดูไหม)
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    # 2. ดึง Logs
    return get_quotation_audit_logs(db, quotation_id=quotation_id)

@router.get("/no/{quotation_no}/versions", response_model=List[Quotation])
def read_quotation_versions(
    quotation_no: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    ดึงรายการเวอร์ชันทั้งหมดของเลขที่ใบเสนอราคา (ใช้สำหรับหน้า History หรือ Version Switcher)
    """
    
    versions = crud_get_versions(db, quotation_no=quotation_no)
    
    if not versions:
        raise HTTPException(
            status_code=404, 
            detail=f"No quotations found for number: {quotation_no}"
        )
        
    return versions

@router.post("/{quotation_id}/notes", response_model=QuotationNoteSchema) # ใช้ Schema
def add_quotation_note(
    quotation_id: int,
    note_in: QuotationNoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    เพิ่ม Note ใหม่ (ไม่สามารถแก้ไขได้ในภายหลัง)
    """
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
        
    # เรียกใช้ CRUD เพื่อบันทึกลง DB และ Audit Log
    return crud_create_quotation_note(db, quotation_id, note_in, current_user)

@router.get("/{quotation_id}/notes", response_model=List[QuotationNoteSchema])
def list_quotation_notes(quotation_id: int, db: Session = Depends(get_db)):
    """
    ดึงรายการ Note ทั้งหมดของใบเสนอราคาผ่าน CRUD
    """
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
        
    return get_quotation_notes(db, quotation_id=quotation_id)

@router.post("/{quotation_id}/attachments", response_model=QuotationAttachmentSchema, status_code=201)
async def upload_quotation_attachment(
    quotation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(PermissionChecker("edit_quotation"))
):
    # 1. เช็ค Quotation
    db_quotation = get_quotation(db, quotation_id=quotation_id)

    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    # 2. บันทึกผ่าน CRUD (ตัว Schema จะจัดการเรื่อง URL ให้เอง)
    return crud_upload_quotation_attachment(
        db=db, 
        quotation_id=quotation_id, 
        file=file, 
        username=current_user.full_name
    )

@router.delete("/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(PermissionChecker("edit_quotation"))
):
    success = crud_delete_quotation_attachment(db, attachment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    return {"message": "File deleted successfully"}

@router.get("/{quotation_id}/attachments", response_model=List[QuotationAttachmentSchema])
async def list_quotation_attachments(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(PermissionChecker("view_quotation"))
):
    # 1. เช็คก่อนว่า Quotation มีอยู่จริงไหม (ใช้ฟังก์ชัน get_quotation เดิมที่คุณมี)
    db_quotation = get_quotation(db, quotation_id=quotation_id)
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    # 2. ดึงรายการไฟล์
    attachments = get_quotation_attachments(db, quotation_id=quotation_id)
    return attachments

@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(PermissionChecker("view_quotation")) # เช็คสิทธิ์ก่อนโหลด
):
    # 1. ค้นหาข้อมูลใน DB
    db_attachment = get_attachment_by_id(db, attachment_id)
    if not db_attachment:
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ที่ต้องการ")

    # 2. ต่อ Path จริงในเครื่อง 
    full_path = UPLOAD_BASE_DIR / db_attachment.file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="ไฟล์ไม่มีอยู่บน Server")

    # 3. ส่งไฟล์กลับไปให้ดาวน์โหลด
    # filename=... จะเป็นชื่อไฟล์ที่ User เห็นตอนโหลดเสร็จ
    return FileResponse(
        path=str(full_path), 
        filename=db_attachment.file_name,
        media_type='application/octet-stream'
    )

@router.post("/items/{item_id}/images")
async def upload_multiple_images(
    item_id: int, 
    files: list[UploadFile] = File(...), # รับเป็นลิสต์ของไฟล์
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_item = db.query(QuotationItem).filter(QuotationItem.id == item_id, QuotationItem.deleted_at == None).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for file in files:
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"ไฟล์ {file.filename} ใหญ่เกินไป (จำกัดไม่เกิน 5MB)"
            )

    return crud_upload_item_images(db, item_id, files, current_user.full_name)

@router.delete("/items/images/{image_id}", response_model=QuotationItemImageSchema)
async def delete_item_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    db_image = crud_soft_delete_item_image(db, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image

@router.patch("/{quotation_no}/external-sync")
def sync_external_status(
    quotation_no: str,
    qo_id: Optional[str] = Body(None),
    qo_no: Optional[str] = Body(None),
    so_no: Optional[str] = Body(None),
    inv_no: Optional[str] = Body(None),
    status: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint ให้ระบบอื่นเรียกเพื่ออัปเดตสถานะกลับมาที่ Quotation
    """
    db_quotation = db.query(Quotation).filter(Quotation.quotation_no == quotation_no).first()
    
    if not db_quotation:
        raise HTTPException(status_code=404, detail="ไม่พบใบเสนอราคาที่ระบุ")

    # อัปเดตข้อมูล Reference
    if qo_id: db_quotation.external_qo_id = qo_id
    if qo_no: db_quotation.external_qo_no = qo_no
    if so_no: db_quotation.external_so_no = so_no
    if inv_no: db_quotation.external_inv_no = inv_no
    if status: db_quotation.external_system_status = status
    
    db_quotation.external_last_update = datetime.now()
    
    # ถ้าสถานะภายนอกเป็น 'Invoiced' หรือ 'Paid' อาจจะปรับ status ภายในเป็น 'win' อัตโนมัติ
    if status in ["Invoiced", "Paid"]:
        db_quotation.status = "win"

    db.commit()
    return {"message": "Status synchronized successfully", "quotation_no": quotation_no}