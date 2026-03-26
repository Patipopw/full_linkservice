from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime, func, and_
from sqlalchemy.orm import relationship
from app.models.base import Base

class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # เชื่อมกลับไปที่ใบเสนอราคาหลัก (Parent)
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    item_no = Column(Integer, nullable=False)  
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)     
    product_name= Column(String, nullable=True)        
    product_part= Column(String, nullable=True)        
    product_description = Column(Text, nullable=False)     
    red_note = Column(Text, nullable=True)     
    quantity = Column(Numeric(12, 2), default=1.00, nullable=False)
    unit = Column(String, nullable=True)           
    rent_duration = Column(String, nullable=True)           
    rent_period = Column(String, nullable=True)          
    
   
    price = Column(Numeric(15, 2), default=0.00, nullable=False)
    vendor = Column(String, nullable=True)           
    cost = Column(Numeric(15, 2), default=0.00, nullable=False)
    discount_item = Column(Numeric(15, 2), default=0.00)             
    total_item_price = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    remark = Column(Text, nullable=True)

    # ความสัมพันธ์ (Relationship)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),  onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    product = relationship("Product") 
    quotation = relationship("Quotation", back_populates="items")
    images = relationship(
        "QuotationItemImage", 
        primaryjoin="and_(QuotationItem.id==QuotationItemImage.item_id, QuotationItemImage.deleted_at==None)",
        back_populates="item", 
        cascade="all, delete-orphan"
    )


class QuotationItemImage(Base):
    __tablename__ = "quotation_item_images"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("quotation_items.id", ondelete="CASCADE"), index=True)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False) # เก็บ path เช่น uploads/quotations/1/items/10/img.jpg
    file_type = Column(String(50))
    uploaded_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    item = relationship("QuotationItem", back_populates="images")