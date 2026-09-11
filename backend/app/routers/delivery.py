from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.get("/requests/available")
def get_available_delivery_requests(university_id: int, db: Session = Depends(get_db)):
    try:
        # Fetch requests that are pending/available and match the university via pickup location
        requests = (
            db.query(models.DeliveryRequest)
            .join(models.Location, models.DeliveryRequest.pickup_location_id == models.Location.id)
            .filter(models.Location.university_id == university_id)
            .filter(models.DeliveryRequest.status == "pending") # Adjust if your initial status string differs
            .all()
        )
        
        # Format response safely to ensure total_fee or other UI fields don't trigger serialization errors
        results = []
        for req in requests:
            results.append({
                "id": req.id,
                "pickup_location_id": req.pickup_location_id,
                "dropoff_location_id": req.dropoff_location_id,
                "reward": req.reward,
                "tip": getattr(req, "tip", 0),
                "total_fee": (req.reward or 0) + getattr(req, "tip", 0),
                "description": getattr(req, "description", "")
            })
        return results
    except Exception as e:
        print(f"Error fetching available jobs: {e}")
        # Fallback to return all pending requests if the location join fails
        fallback_requests = db.query(models.DeliveryRequest).filter_by(status="pending").all()
        return [{
            "id": r.id,
            "pickup_location_id": r.pickup_location_id,
            "dropoff_location_id": r.dropoff_location_id,
            "reward": r.reward,
            "tip": 0,
            "total_fee": r.reward,
            "description": getattr(r, "description", "")
        } for r in fallback_requests]