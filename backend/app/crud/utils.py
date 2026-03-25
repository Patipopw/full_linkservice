from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def create_audit_log(
    db: Session, 
    target_type: str, 
    target_id: int, 
    action: str, 
    user: any, 
    changes: dict = None, 
    doc_no: str = None
):
    """
    ฟังก์ชันกลางสำหรับบันทึก Audit Log ลงฐานข้อมูล
    """
    log_entry = AuditLog(
        target_type=target_type,
        target_id=target_id,
        document_no=doc_no,
        action=action,
        changes=changes,
        changed_by=user.full_name or user.email,
        changed_by_id=str(user.id)
    )
    db.add(log_entry)
    # ไม่ต้อง db.commit() ที่นี่ เพราะมักจะใช้ร่วมกับ Transaction ของข้อมูลหลัก
