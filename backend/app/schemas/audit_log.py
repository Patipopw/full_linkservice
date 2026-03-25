from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict

class AuditLogSchema(BaseModel):
    id: int
    target_type: str
    target_id: int
    document_no: Optional[str] = None
    action: str
    changes: Optional[Dict[str, Any]] = None  # รองรับ JSON object ที่เราเก็บ
    changed_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
