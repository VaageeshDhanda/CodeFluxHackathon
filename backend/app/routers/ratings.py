# backend/app/routers/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .. import models
from ..database import get_db

router = APIRouter(prefix="/ratings", tags=["Ratings & Trust"])

class RatingCreate(BaseModel):
    rater_id: int
    ratee_id: int
    job_id: int
    score: int = Field(..., ge=1, le=5)
    feedback: str = ""

@router.post("/")
def submit_rating(req: RatingCreate, db: Session = Depends(get_db)):
    # Enforce Rule: A rating should not be submitted repeatedly for the same eligible event[cite: 3].
    existing = db.query(models.Rating).filter(
        models.Rating.rater_id == req.rater_id,
        models.Rating.job_id == req.job_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already rated this transaction")

    new_rating = models.Rating(
        rater_id=req.rater_id,
        ratee_id=req.ratee_id,
        job_id=req.job_id,
        score=req.score,
        feedback=req.feedback
    )
    
    db.add(new_rating)
    db.commit()
    
    return {"status": "success", "message": "Rating submitted successfully"}