from pydantic import BaseModel, Field
from typing import Optional
from .models import DeliveryStatus, RequestSourceType, PaymentMethod

class UniversityBase(BaseModel):
    name: str

class UniversityResponse(UniversityBase):
    id: int

    class Config:
        from_attributes = True

class LocationBase(BaseModel):
    name: str
    university_id: int

class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    university_id: int
    is_admin: Optional[bool] = False

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    university_id: int
    is_admin: bool

    class Config:
        from_attributes = True

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

class JobAcceptRequest(BaseModel):
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class MarketplaceListingCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str

    class Config:
        from_attributes = True

class MarketplaceListingResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    category: str
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