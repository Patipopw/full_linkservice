from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # เพิ่ม index=True เพื่อให้ค้นหาประวัติรายเอกสารได้เร็วขึ้น
    target_type = Column(String, index=True) # "quotation", "sale_order"
    target_id = Column(Integer, index=True)   # ID ของเอกสาร
    document_no = Column(String, index=True)  # เลขที่เอกสาร (QT24001)
    
    action = Column(String)      # "CREATE", "UPDATE", "APPROVE"
    changes = Column(JSON)       # เก็บข้อมูลความเปลี่ยนแปลงเป็น JSON
    
    changed_by = Column(String)
    changed_by_id = Column(String)
    
    # ใช้ server_default=func.now() เพื่อให้ DB เป็นคนลงเวลาให้เอง
    created_at = Column(DateTime(timezone=True), server_default=func.now())
