# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .models import DeliveryStatus, RequestSourceType

class DeliveryRequestCreate(BaseModel):
    requester_id: int
    pickup_location_id: int
    drop_location_id: int
    source_type: RequestSourceType = RequestSourceType.EXTERNAL_PARCEL
    description: Optional[str] = None
    order_reference: Optional[str] = None
    distance_fee: float = Field(default=0.0, ge=0.0) # Calculated by a map service or UI for now
    tip: float = Field(default=0.0, ge=0.0)

class DeliveryRequestResponse(BaseModel):
    id: int
    university_id: int
    status: DeliveryStatus
    total_fee: float
    created_at: datetime

    class Config:
        orm_mode = True

class JobAcceptRequest(BaseModel):
    partner_id: int

class OTPVerification(BaseModel):
    job_id: int
    otp_code: str

# Add to backend/app/schemas.py

class MarketplaceListingCreate(BaseModel):
    seller_id: int
    item_name: str
    description: Optional[str] = None
    reference_price: float
    listing_price: float
    quantity: int = Field(default=1, ge=1)
    location_id: int

class TransactionCreate(BaseModel):
    buyer_id: int
    listing_id: int
    quantity: int = Field(default=1, ge=1)
    delivery_requested: bool
    drop_location_id: Optional[int] = None # Required if delivery_requested is True    