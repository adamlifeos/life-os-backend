from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from ..database import get_db
from ..models import Identity, Skill, Habit
from ..schemas.item_schemas import PositionUpdate, SectionUpdate, BatchUpdate, ItemResponse
from ..auth import get_current_user

router = APIRouter(prefix="/items", tags=["items"])

MODEL_MAP = {
    "identities": Identity,
    "skills": Skill,
    "habits": Habit
}

def get_item_model(item_id: int, db: Session):
    """Get the correct model instance based on item_id"""
    for model in MODEL_MAP.values():
        item = db.query(model).filter(model.id == item_id).first()
        if item:
            return item, model
    raise HTTPException(status_code=404, detail="Item not found")

@router.patch("/{item_id}/position", response_model=ItemResponse)
async def update_position(
    item_id: int,
    position: PositionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    item, _ = get_item_model(item_id, db)
    
    # Verify ownership
    if hasattr(item, "user_id") and item.user_id != current_user.id:
        if hasattr(item, "identity") and item.identity.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this item")
    
    # Update position
    item.x = position.x
    item.y = position.y
    db.commit()
    
    return {"id": item_id, "success": True}

@router.patch("/{item_id}/section", response_model=ItemResponse)
async def update_section(
    item_id: int,
    update: SectionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    item, source_model = get_item_model(item_id, db)
    target_model = MODEL_MAP[update.new_section]
    
    # Verify ownership
    if hasattr(item, "user_id") and item.user_id != current_user.id:
        if hasattr(item, "identity") and item.identity.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this item")
    
    # Update section and position
    if source_model != target_model:
        raise HTTPException(status_code=400, detail="Cannot change item type")
    
    # Update position within section
    item.position = update.position
    db.commit()
    
    return {"id": item_id, "success": True}

@router.post("/batch", response_model=List[ItemResponse])
async def batch_update(
    updates: BatchUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    responses = []
    
    for item_id, update in zip(updates.item_ids, updates.updates):
        try:
            item, _ = get_item_model(item_id, db)
            
            # Verify ownership
            if hasattr(item, "user_id") and item.user_id != current_user.id:
                if hasattr(item, "identity") and item.identity.user_id != current_user.id:
                    raise HTTPException(status_code=403, detail="Not authorized to update this item")
            
            # Apply updates
            if "x" in update and "y" in update:
                item.x = update["x"]
                item.y = update["y"]
            elif "new_section" in update and "position" in update:
                item.position = update["position"]
            
            responses.append({"id": item_id, "success": True})
        except Exception as e:
            responses.append({"id": item_id, "success": False, "message": str(e)})
    
    db.commit()
    return responses
