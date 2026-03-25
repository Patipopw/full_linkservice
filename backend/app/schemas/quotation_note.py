from pydantic import BaseModel, ConfigDict
from datetime import datetime

class QuotationNoteBase(BaseModel):
    note_text: str

class QuotationNoteCreate(QuotationNoteBase):
    pass

class QuotationNote(QuotationNoteBase):
    id: int
    quotation_id: int
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
