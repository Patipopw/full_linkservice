from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Company(Base):
    __tablename__ = "companies"

    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)

    # --- External Mapping (TRCloud / อื่นๆ) ---
    trcloud_id = Column(String(100), unique=True, index=True, nullable=True) 
    # code_number จาก TRCloud
    code_number = Column(String(100), unique=True, index=True, nullable=True)

    # --- ข้อมูลนิติบุคคล (อ้างอิงตาม Data TRCloud) ---
    name = Column(String(255), nullable=False)        # จาก 'organization'
    branch_code = Column(String(10), default="00000") # จาก 'branch' (สำคัญมากสำหรับภาษีไทย)
    tax_id = Column(String(20), index=True)           # จาก 'tax_id'
    address = Column(Text)                            # จาก 'address'
    
    # --- ข้อมูลการติดต่อ (สำหรับหัวกระดาษ Quotation) ---
    phone = Column(String(50), nullable=True)         # จาก 'telephone'
    email = Column(String(100), nullable=True)        # จาก 'email'

    # --- สถานะและการควบคุม ---
    is_active = Column(Boolean, default=True, server_default="true")
    
    # --- Relationships ---
    quotations = relationship("Quotation", back_populates="company")
    contacts = relationship("CompanyContact", back_populates="company", cascade="all, delete-orphan")

    # --- Audit Trail ---
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class CompanyContact(Base):
    __tablename__ = "company_contacts"

    id = Column(Integer, primary_key=True, index=True)
    # เชื่อมโยงกลับไปหา Company
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # ข้อมูลจาก TRCloud Contact Person
    contact_id = Column(Integer, index=True) # เลข ID 199 จาก TRCloud
    name = Column(String(255), nullable=False) # เจนจิรา
    email = Column(String(255))               # info@trcloud.co
    phone = Column(String(255))               # 023701250 (เดิมคือ telephone)
    position = Column(String(255))            # ฝ่ายจัดซื้อ

    # Relationship
    company = relationship("Company", back_populates="contacts")

    # --- Audit Trail ---
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
