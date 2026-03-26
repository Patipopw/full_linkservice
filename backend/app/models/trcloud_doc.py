from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, func, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

class TRCloudDocMixin:
    """ ฟิลด์มาตรฐานสำหรับเอกสารที่ Sync มาจาก TRCloud """
    id = Column(Integer, primary_key=True, index=True)
    trcloud_id = Column(String(100), index=True, unique=True) # ID จริงใน TRCloud
    company_format = Column(String(50), index=True, nullable=False)   # 
    document_number = Column(String(50), index=True, nullable=False)   # 
    status = Column(String(50))                               # สถานะ (Open, Partial, Closed, Void)
    
    # เก็บข้อมูลดิบจาก TRCloud เผื่อต้องไล่ดูภายหลัง
    head = Column(JSON, nullable=True) 
    body = Column(JSON, nullable=True) 
    
    external_last_update = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SaleOrder(Base, TRCloudDocMixin):
    __tablename__ = "tr_sale_orders"
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="SET NULL"))
    
class PurchaseRequest(Base, TRCloudDocMixin):
    __tablename__ = "tr_purchase_requests"
    vendor_name = Column(String(255))
    so_id = Column(Integer, ForeignKey("tr_sale_orders.id", ondelete="SET NULL"))

class PurchaseOrder(Base, TRCloudDocMixin):
    __tablename__ = "tr_purchase_orders"
    vendor_name = Column(String(255))
    so_id = Column(Integer, ForeignKey("tr_sale_orders.id", ondelete="SET NULL"))
    pr_id = Column(Integer, ForeignKey("tr_purchase_requests.id", ondelete="SET NULL"))

class GoodReceive(Base, TRCloudDocMixin):
    __tablename__ = "tr_good_receives"
    po_id = Column(Integer, ForeignKey("tr_purchase_orders.id", ondelete="SET NULL"))


class MaterialRequest(Base, TRCloudDocMixin):
    __tablename__ = "tr_material_requests"
    so_id = Column(Integer, ForeignKey("tr_sale_orders.id", ondelete="SET NULL"))

class Invoice(Base, TRCloudDocMixin):
    __tablename__ = "tr_invoices"
    so_id = Column(Integer, ForeignKey("tr_sale_orders.id", ondelete="SET NULL"))
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="SET NULL"))


class WebhookLog(Base):
  __tablename__ = "webhook_logs"
  
  id = Column(Integer, primary_key=True, index=True)
  engine = Column(String, index=True)
  action = Column(String, index=True)
  payload = Column(String) 
  received_at = Column(DateTime(timezone=True), server_default=func.now())