from sqlalchemy.orm import Session
from app.models.trcloud_doc import WebhookLog
from sqlalchemy import desc
from typing import Any
import datetime

# --- CREATE: บันทึก Webhook ใหม่ ---
def create_webhook_log(db: Session, payload_str: str, engine_type: str, action_type: str):
    """
    บันทึก JSON ที่ได้รับจาก TRCloud ลงฐานข้อมูล
    """
    db_log = WebhookLog(
        payload=payload_str,
        engine_type=engine_type,
        action_type=action_type,
        status="received" # ตั้งสถานะเริ่มต้น
    )
    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        raise e

# --- READ: ดึงข้อมูลตาม ID ---
def get_webhook_log(db: Session, log_id: int):
    return db.query(WebhookLog).filter(WebhookLog.id == log_id).first()

# --- READ: ดึงรายการทั้งหมด (เรียงจากใหม่ไปเก่า) ---
def get_webhook_logs(db: Session, skip: int = 0, limit: int = 50):
    return db.query(WebhookLog)\
             .order_by(desc(WebhookLog.received_at))\
             .offset(skip)\
             .limit(limit)\
             .all()

# --- DELETE: ลบ Log เก่า (ถ้าจำเป็น) ---
def delete_webhook_log(db: Session, log_id: int):
    db_log = get_webhook_log(db, log_id)
    if db_log:
        db.delete(db_log)
        db.commit()
        return True
    return False


def upsert_document(db: Session, model_class, id_field: str, data: dict):
    """ทำทั้ง Create และ Update ในฟังก์ชันเดียว"""
    api_id = data.get(id_field)
    
    # ค้นหา Record เดิม
    existing = db.query(model_class).filter(
        getattr(model_class, id_field) == api_id,
        model_class.deleted_at == None
    ).first()

    new_obj = model_class(**data)
    if existing:
        new_obj.id = existing.id  # สวม ID เดิมเพื่อทำการ Update (Merge)
    
    db.merge(new_obj)
    db.commit()
    return "Edit" if existing else "Create"

def soft_delete_document(db: Session, model_class, id_field: str, doc_id: str):
    """จัดการ Soft Delete"""
    existing = db.query(model_class).filter(
        getattr(model_class, id_field) == doc_id,
        model_class.deleted_at == None
    ).first()

    if existing:
        existing.deleted_at = datetime.now()
        db.commit()
        return True
    return False