import enum
from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, Date, DateTime, func, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from app.models.base import Base

class QuotationStatus(str, enum.Enum):
    DRAFT = "draft"
    QUOTATION = "quotation"
    WIN = "win"
    LOST = "lost"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"

class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)

    quotation_no = Column(String, index=True, nullable=False)
    version = Column(Integer, default=0, nullable=False, index=True)
    # quotation_no = Column(String, unique=True, index=True, nullable=False)
    status = Column(
        Enum(QuotationStatus, native_enum=False), 
        default=QuotationStatus.DRAFT,
        nullable=False,
        index=True
    )
    company_name = Column(String, nullable=False)
    company_address = Column(Text, nullable=True)
    customer_name = Column(String, nullable=False)
    customer_tel = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    quotation_date = Column(Date, nullable=False, server_default=func.current_date()) 
    validity_date = Column(Date, nullable=False)
    sale_name = Column(String, nullable=False)
    position = Column(String, nullable=True)
    sale_tel = Column(String, nullable=True)
    sale_email = Column(String, nullable=True)
    ref_no = Column(String, nullable=True)
    serial_no = Column(String, nullable=True)
    remark = Column(Text, nullable=True)
    discount = Column(Numeric(10, 2), default=0.00) 
    vat = Column(Numeric(10, 2), default=7.00) 
    total_amount = Column(Numeric(15, 2), default=0.00)
    creator = Column(String, nullable=False)
    creator_id = Column(String, nullable=False)
    sale_id = Column(String, nullable=False)
    signature = Column(String, nullable=True)
    project_name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    subcategory = Column(String, nullable=True)
    notice = Column(Text, nullable=True)


    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),  onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('quotation_no', 'version', name='uq_quotation_no_version'),
        Index('idx_quotation_no_version_deleted', 'quotation_no', 'version', 'deleted_at'),
    )
    notes = relationship("QuotationNote", back_populates="quotation", cascade="all, delete-orphan")
    attachments = relationship("QuotationAttachment", back_populates="quotation") 


class QuotationAttachment(Base):
    __tablename__ = "quotation_attachments"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="CASCADE"), index=True)
    
    file_name = Column(String(255), nullable=False) # ชื่อไฟล์เดิม (เช่น document.pdf)
    file_path = Column(String(500), nullable=False) # Path ที่เก็บไฟล์จริงบน Server
    file_type = Column(String(50))                  # MIME type (เช่น application/pdf)
    file_size = Column(Integer)                     # ขนาดไฟล์ (bytes)
    
    uploaded_by = Column(String)                    # ชื่อ user ที่อัปโหลด
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # Relationship กลับไปที่ Quotation หลัก
    quotation = relationship("Quotation", back_populates="attachments")
