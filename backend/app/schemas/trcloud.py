from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import  Any, Optional

class WebhookLogBase(BaseModel):
    payload: Any           # เก็บ JSON ที่ส่งมาทั้งหมด
    engine_type: Optional[str] = None  # เช่น 'so', 'iv', 'po'
    action_type: Optional[str] = None  # เช่น 'create', 'edit', 'delete'
    status: str = "received"           # 'received', 'processed', 'failed'


class WebhookLogCreate(WebhookLogBase):
  pass # Used when saving the incoming webhook

class WebhookLog(WebhookLogBase):
  id: int
  received_at: datetime

  model_config = ConfigDict(from_attributes=True)

class TRModel(BaseModel):
    id: int
    company_id: int
    time: int
    hash: str