from fastapi import APIRouter, Depends, HTTPException, Request, Header, status, BackgroundTasks, Form
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from typing import  Annotated
import json
from app.api.endpoints.trcloud.connector import verify_hash
from app.crud.trcloud import create_webhook_log, get_webhook_logs
from app.schemas.trcloud import WebhookLog, TRModel
from app.tasks.trcloud import handle_document

router = APIRouter()

@router.get("/status")
def webhook_status():
    return {"status": "webhook receiver is active"}

@router.post("/trcloud", status_code=status.HTTP_200_OK)
async def handle_trcloud_webhook(
    data: Annotated[TRModel, Form()],
    request: Request,
    background_tasks: BackgroundTasks, # 1. เพิ่ม BackgroundTasks
    action: str = "",
    engine: str = "",
    db: Session = Depends(get_db)
):
  try:
    trc_model = data.model_dump(exclude_unset=True)
    payload_str = json.dumps(trc_model, ensure_ascii=False)

    # 2. บันทึก Log ลงฐานข้อมูลทันที
    new_log = create_webhook_log(db=db, 
      payload_str=payload_str,
      engine_type=engine, 
      action_type=action)

    # 3. Verify
    if not verify_hash(request, trc_model):
      # print(f"❌ Hash Mismatch!")
      # print(f"Received: {trc_model.get('hash')}")
      raise HTTPException(status_code=400, detail="Hash verification failed")

    # 4. โยนงานประมวลผล Business Logic ไปที่ Background
    background_tasks.add_task(handle_document, trc_model.get('id'), engine, action)

    return {
        "status": "success", 
        "log_id": new_log.id, 
        "message": "Webhook received"
    }

  except HTTPException as he:
    raise he
  except Exception as e:
    # หากบันทึก Log ไม่สำเร็จ หรือเกิด Error อื่นๆ
    print(f"🚨 Webhook Error: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        detail="Internal Server Error"
    )

@router.get("/logs", response_model=list[WebhookLog])
def get_all_webhook_logs(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    # This calls a CRUD function to see what was received
    return get_webhook_logs(db=db, skip=skip, limit=limit)