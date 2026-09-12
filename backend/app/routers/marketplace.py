from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import models
from ..database import get_db

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

class ListingCreate(BaseModel):
    seller_id: int
    item_name: str
    description: str = ""
    reference_price: float
    listing_price: float
    quantity: int = 1
    location_id: int

@router.post("/listings")
def create_listing(req: ListingCreate, db: Session = Depends(get_db)):
    max_allowed_price = req.reference_price * 1.5
    if req.listing_price > max_allowed_price:
        raise HTTPException(
            status_code=400, 
            detail=f"Listing price exceeds maximum allowed 1.5x cap (Max: ₹{max_allowed_price})"
        )

    new_listing = models.MarketplaceListing(
        seller_id=req.seller_id,
        item_name=req.item_name,
        description=req.description,
        reference_price=req.reference_price,
        listing_price=req.listing_price,
        quantity=req.quantity,
        location_id=req.location_id,
        status=models.MarketplaceStatus.ACTIVE
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

@router.get("/listings")
def get_active_listings(university_id: int, db: Session = Depends(get_db)):
    listings = db.query(models.MarketplaceListing).filter(
        models.MarketplaceListing.status == models.MarketplaceStatus.ACTIVE
    ).all()
    return listings

@router.get("/user/{user_id}/listings")
def get_user_listings(user_id: int, db: Session = Depends(get_db)):
    listings = db.query(models.MarketplaceListing).filter(models.MarketplaceListing.user_id == user_id).all()
    
    active = [item for item in listings if item.status == "active" or item.status == "available"]
    expired = [item for item in listings if item.status == "expired"]
    completed = [item for item in listings if item.status == "completed"]
    
    return {
        "active": active,
        "expired": expired,
        "completed": completed
    }