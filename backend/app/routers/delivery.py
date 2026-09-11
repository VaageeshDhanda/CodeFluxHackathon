from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.post("/requests")
def create_delivery_request(payload: schemas.DeliveryRequestCreate, db: Session = Depends(get_db)):
    try:
        new_request = models.DeliveryRequest(
            requester_id=payload.requester_id,
            description=payload.description,
            pickup_location_id=payload.pickup_location_id,
            dropoff_location_id=payload.dropoff_location_id,
            reward=payload.reward,
            source_type=payload.source_type,
            tip=getattr(payload, "tip", 0),
            status="pending"
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return {"message": "Delivery requested successfully", "id": new_request.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))