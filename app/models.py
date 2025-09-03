from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

DocType = Literal["invoice","unknown"]

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    source_bbox: Optional[List[float]] = None  # [x1,y1,x2,y2] normalized

class NormalizedDoc(BaseModel):
    doc_type: DocType
    currency: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    supplier_name: Optional[str] = None
    total_amount: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)
    confidence: float = 0.0
    trace: Dict[str, Any] = Field(default_factory=dict)  # field→span id, page idx, bbox

class ExtractResult(BaseModel):
    used_model: str
    raw_ocr: dict
