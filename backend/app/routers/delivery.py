from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.post("/requests")
def create_delivery_request(payload: schemas.DeliveryRequestCreate, db: Session = Depends(get_db)):
    try:
        new_job = models.DeliveryJob(
            user_id=payload.requester_id,
            description=payload.description,
            pickup_location_id=payload.pickup_location_id,
            dropoff_location_id=payload.dropoff_location_id,
            reward=payload.reward,
            status="pending"
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return {"message": "Delivery requested successfully", "id": new_job.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/requests/available")
def get_available_delivery_requests(university_id: int, db: Session = Depends(get_db)):
    try:
        jobs = (
            db.query(models.DeliveryJob)
            .join(models.Location, models.DeliveryJob.pickup_location_id == models.Location.id)
            .filter(models.Location.university_id == university_id)
            .filter(models.DeliveryJob.status == "pending")
            .all()
        )
        
        results = []
        for job in jobs:
            results.append({
                "id": job.id,
                "pickup_location_id": job.pickup_location_id,
                "dropoff_location_id": job.dropoff_location_id,
                "reward": job.reward,
                "tip": getattr(job, "tip", 0),
                "total_fee": (job.reward or 0) + getattr(job, "tip", 0),
                "description": getattr(job, "description", "")
            })
        return results
    except Exception as e:
        print(f"Error fetching available jobs: {e}")
        fallback_jobs = db.query(models.DeliveryJob).filter_by(status="pending").all()
        return [{
            "id": j.id,
            "pickup_location_id": j.pickup_location_id,
            "dropoff_location_id": j.dropoff_location_id,
            "reward": j.reward,
            "tip": 0,
            "total_fee": j.reward,
            "description": getattr(j, "description", "")
        } for j in fallback_jobs]

@router.post("/jobs/{job_id}/accept")
def accept_delivery_job(job_id: int, payload: schemas.JobAcceptRequest, db: Session = Depends(get_db)):
    job = db.query(models.DeliveryJob).filter(models.DeliveryJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "pending":
        raise HTTPException(status_code=400, detail="Job is no longer available")
    
    job.status = "accepted"
    db.commit()
    db.refresh(job)
    return {"message": "Job accepted successfully", "demo_otp_revealed": "1234"}