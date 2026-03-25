from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class QuotationNote(Base):
    __tablename__ = "quotation_notes"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="CASCADE"), index=True)
    note_text = Column(Text, nullable=False)
    created_by = Column(String)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quotation = relationship("Quotation", back_populates="notes")