from pydantic import BaseModel
from typing import List, Literal

class PositionUpdate(BaseModel):
    x: float
    y: float

class SectionUpdate(BaseModel):
    new_section: Literal["identities", "skills", "habits"]
    position: int  # Order within section

class BatchUpdate(BaseModel):
    item_ids: List[int]
    updates: List[dict]  # List of position or section updates

class ItemResponse(BaseModel):
    id: int
    success: bool
    message: str = "Update successful"
