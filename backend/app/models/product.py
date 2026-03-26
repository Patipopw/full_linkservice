from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, func, Boolean
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    
    # สำหรับเชื่อมโยงกับระบบอื่น (External System ID)
    external_id = Column(String(100), unique=True, index=True, nullable=True)
    
    # ข้อมูลสินค้า
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=True)
    
    # ราคามาตรฐาน
    standard_price = Column(Numeric(15, 2), default=0.00)
    cost = Column(Numeric(15, 2), default=0.00)
    unit = Column(String(50), nullable=True)
    
    # สถานะ
    is_active = Column(Boolean, default=True)
    image_url = Column(String(500), nullable=True)
    
    # Audit Trail
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
