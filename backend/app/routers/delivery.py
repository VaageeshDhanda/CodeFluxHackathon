# backend/app/routers/delivery.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import random
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/delivery", tags=["Delivery Engine"])

@router.post("/requests", response_model=schemas.DeliveryRequestResponse)
def create_delivery_request(req: schemas.DeliveryRequestCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == req.requester_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Requester not found")

    # Authoritative backend pricing calculation: ₹10 Base + Distance + Tip
    base_fee = 10.0
    total_fee = base_fee + req.distance_fee + req.tip

    new_request = models.DeliveryRequest(
        university_id=user.university_id,
        requester_id=user.id,
        source_type=req.source_type,
        pickup_location_id=req.pickup_location_id,
        drop_location_id=req.drop_location_id,
        description=req.description,
        order_reference=req.order_reference,
        base_fee=base_fee,
        distance_fee=req.distance_fee,
        tip=req.tip,
        total_fee=total_fee,
        status=models.DeliveryStatus.AVAILABLE
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("/requests/available")
def get_available_jobs(university_id: int, db: Session = Depends(get_db)):
    # Returns all unaccepted jobs for a specific university campus
    jobs = db.query(models.DeliveryRequest).filter(
        models.DeliveryRequest.status == models.DeliveryStatus.AVAILABLE,
        models.DeliveryRequest.university_id == university_id
    ).all()
    return jobs

@router.post("/jobs/{request_id}/accept")
def accept_delivery_job(request_id: int, accept_req: schemas.JobAcceptRequest, db: Session = Depends(get_db)):
    delivery_req = db.query(models.DeliveryRequest).filter(models.DeliveryRequest.id == request_id).first()
    
    if not delivery_req or delivery_req.status != models.DeliveryStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Job is not available")

    # Enforce Rule: Partner must have <= 3 active parcels
    active_jobs = db.query(models.DeliveryJob).filter(
        models.DeliveryJob.partner_id == accept_req.partner_id,
        models.DeliveryJob.status.in_([models.DeliveryStatus.ACCEPTED, models.DeliveryStatus.PICKED_UP, models.DeliveryStatus.OUT_FOR_DELIVERY])
    ).count()
    
    if active_jobs >= 3:
        raise HTTPException(status_code=403, detail="Maximum 3 active parcels allowed")

    # Generate 4-digit OTP and hash it for security
    raw_otp = str(random.randint(1000, 9999))
    otp_hash = hashlib.sha256(raw_otp.encode()).hexdigest()

    # Create the job and update request status
    new_job = models.DeliveryJob(
        delivery_request_id=delivery_req.id,
        partner_id=accept_req.partner_id,
        status=models.DeliveryStatus.ACCEPTED,
        otp_hash=otp_hash
    )
    delivery_req.status = models.DeliveryStatus.ACCEPTED
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # In a real app, send raw_otp via push notification to the recipient here
    return {"job_id": new_job.id, "message": "Job accepted", "demo_otp_revealed": raw_otp}

@router.post("/jobs/complete")
def complete_delivery(verification: schemas.OTPVerification, db: Session = Depends(get_db)):
    job = db.query(models.DeliveryJob).filter(models.DeliveryJob.id == verification.job_id).first()
    
    if not job or job.status == models.DeliveryStatus.DELIVERED:
        raise HTTPException(status_code=400, detail="Invalid job or already delivered")

    # Validate OTP
    submitted_hash = hashlib.sha256(verification.otp_code.encode()).hexdigest()
    if submitted_hash != job.otp_hash:
        job.attempt_count += 1
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # Update states on success
    job.status = models.DeliveryStatus.DELIVERED
    job.delivered_at = datetime.utcnow()
    job.request.status = models.DeliveryStatus.DELIVERED
    
    db.commit()
    return {"status": "success", "message": "Delivery completed successfully"}


@router.get("/jobs/active/{partner_id}")
def get_active_partner_jobs(partner_id: int, db: Session = Depends(get_db)):
    # Fetch all jobs for this partner that are not yet delivered
    jobs = db.query(models.DeliveryJob).filter(
        models.DeliveryJob.partner_id == partner_id,
        models.DeliveryJob.status != models.DeliveryStatus.DELIVERED
    ).all()
    return jobs