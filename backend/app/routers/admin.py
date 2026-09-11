# backend/app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Gather platform statistics for the dashboard
    active_deliveries = db.query(models.DeliveryJob).filter(
        models.DeliveryJob.status != models.DeliveryStatus.DELIVERED
    ).count()
    
    active_listings = db.query(models.MarketplaceListing).filter(
        models.MarketplaceListing.status == models.MarketplaceStatus.ACTIVE
    ).count()
    
    total_payments = db.query(models.Payment).count()
    
    # Fetch all payments to display in the override list
    recent_payments = db.query(models.Payment).order_by(models.Payment.created_at.desc()).limit(10).all()
    
    return {
        "active_deliveries": active_deliveries,
        "active_listings": active_listings,
        "total_payments": total_payments,
        "recent_payments": recent_payments
    }

@router.post("/payments/{payment_id}/override")
def override_payment_state(payment_id: int, db: Session = Depends(get_db)):
    # Admin control to forcefully approve a stuck simulated payment
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    payment.status = models.PaymentStatus.OVERRIDDEN
    db.commit()
    
    return {"status": "success", "message": f"Payment {payment_id} overridden successfully"}