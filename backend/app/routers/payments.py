# backend/app/routers/payments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import random
from .. import models
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["Simulated Payments"])

class PaymentCreate(BaseModel):
    payer_id: int
    payee_id: int
    amount: float
    method: models.PaymentMethod = models.PaymentMethod.SIMULATED_UPI

@router.post("/simulate")
def initiate_simulated_payment(req: PaymentCreate, db: Session = Depends(get_db)):
    # Generate a fake transaction ID for the MVP
    fake_txn_id = f"UPI-{random.randint(100000, 999999)}"
    
    new_payment = models.Payment(
        transaction_id=fake_txn_id,
        payer_id=req.payer_id,
        payee_id=req.payee_id,
        amount=req.amount,
        method=req.method,
        status=models.PaymentStatus.PENDING,
        is_simulated=True
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return {
        "payment_id": new_payment.id, 
        "transaction_id": new_payment.transaction_id,
        "amount": new_payment.amount,
        "qr_data": f"hostlehive://pay?txn={fake_txn_id}&amt={req.amount}"
    }

@router.post("/{payment_id}/complete")
def complete_simulated_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
        
    if payment.status != models.PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Payment is not pending")

    payment.status = models.PaymentStatus.PAID
    db.commit()
    
    return {"status": "success", "message": "Simulated payment successful"}