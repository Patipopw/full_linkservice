from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.api.endpoints.trcloud.connector import trcloud_api_read
from app.crud.trcloud import upsert_document, soft_delete_document
from app import models
import datetime
def dev_log(message):
    # ใช้ settings.ENV แทน os.getenv
    if settings.ENV != "production":
        print(message)

async def handle_document(doc_id: str, engine: str, action: str):
    # Mapping ตามโครงสร้าง TRCloudDocMixin ที่เราทำไว้ (ใช้ trcloud_id เป็นหลัก)
    doc_mapping = {
        "iv": (models.Invoice, "trcloud_id"), 
        "mr": (models.MaterialRequest, "trcloud_id"),
        "gr": (models.GoodReceive, "trcloud_id"),
        "po": (models.PurchaseOrder, "trcloud_id"),
        "pr": (models.PurchaseRequest, "trcloud_id"),
        "so": (models.SaleOrder, "trcloud_id"),
        # "qo": (models.Quotation, "trcloud_id"), # ถ้าคุณใช้ QT ระบบเราเป็นหลัก อาจจะไม่ต้อง Sync กลับ
    }

    if engine not in doc_mapping:
        dev_log(f"❌ Unknown engine: {engine}")
        return

    model_class, id_field = doc_mapping[engine]
    
    # 1. สร้าง Session ใหม่สำหรับ Background Task
    db = SessionLocal()

    try:
        if action in ["create", "edit"]:
            # 2. ดึงข้อมูลเต็มจาก TRCloud API
            res_api = await trcloud_api_read(engine, doc_id)
            if not res_api or res_api.get("status") != "success":
                dev_log(f"⚠️ API Read failed for {engine}: {doc_id}")
                return

            head = res_api.get("head", {})
            
            # 3. เตรียมข้อมูลให้ตรงกับ TRCloudDocMixin
            data_args = {
                "trcloud_id": str(doc_id),
                "company_format": head.get("company_format"),
                "document_number": head.get("document_number") or head.get("invoice_number"),
                "status": head.get("status"),
                "head": head,
                "body": res_api.get("body", []),
                "external_last_update": datetime.datetime.now(),
                "deleted_at": None
            }
            
            # 4. เรียกใช้ Upsert
            status = upsert_document(db, model_class, "trcloud_id", data_args)
            dev_log(f"✅ {status} {engine}: {data_args['document_number']}")

        elif action == "delete":
            # 5. Soft Delete โดยอ้างอิงจาก trcloud_id
            success = soft_delete_document(db, model_class, "trcloud_id", doc_id)
            if success:
                dev_log(f"🗑️ Soft Delete {engine}: {doc_id}")
            else:
                dev_log(f"⚠️ Not found {engine} to delete: {doc_id}")

    except Exception as e:
        db.rollback()
        dev_log(f"🔥 Error in handle_document ({engine}): {str(e)}")
    finally:
        db.close()