from pydantic import BaseModel, ConfigDict, computed_field
from app.core.config import settings
import os

# Schema พื้นฐานสำหรับแสดงผล
class QuotationAttachmentSchema(BaseModel):
    id: int
    quotation_id: int
    file_name: str
    file_path: str # เก็บ path จริงไว้
    # ... ฟิลด์อื่นๆ ...

    @computed_field
    @property
    def file_url(self) -> str:
        # ดึงแค่ชื่อไฟล์ออกมาจาก Path เต็ม แล้วประกอบเป็น URL
        filename = os.path.basename(self.file_path)
        return f"{settings.BACKEND_HOST}/uploads/quotations/{self.file_path}"
    

    model_config = ConfigDict(from_attributes=True)

# Schema สำหรับตอน Create (ถ้าจำเป็นต้องใช้)
class QuotationAttachmentCreate(BaseModel):
    file_name: str
    file_type: str
    file_size: int
