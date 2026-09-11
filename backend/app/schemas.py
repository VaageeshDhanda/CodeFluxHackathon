from pydantic import BaseModel, Field
from typing import Optional
from .models import DeliveryStatus, RequestSourceType, PaymentMethod

class DeliveryRequestCreate(BaseModel):
    description: str
    pickup_location_id: int
    dropoff_location_id: int
    reward: float
    source_type: RequestSourceType = RequestSourceType.EXTERNAL_PARCEL
    tip: float = Field(default=0.0, ge=0.0)

    class Config:
        from_attributes = True

class DeliveryRequestResponse(BaseModel):
    id: int
    description: str
    pickup_location_id: int
    dropoff_location_id: int
    reward: float
    user_id: int
    status: str

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    amount: float
    method: PaymentMethod = PaymentMethod.SIMULATED_UPI
    job_id: Optional[int] = None

    class Config:
        from_attributes = True