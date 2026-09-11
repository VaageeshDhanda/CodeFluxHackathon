# backend/app/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class PaymentMethod(str, enum.Enum):
    SIMULATED_UPI = "SIMULATED_UPI"
    CASH = "CASH"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERRIDDEN = "OVERRIDDEN"

class DeliveryStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ACCEPTED = "ACCEPTED"
    DELIVERED = "DELIVERED"

class MarketplaceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"

class RequestSourceType(str, enum.Enum):
    EXTERNAL_PARCEL = "EXTERNAL_PARCEL"
    MARKETPLACE = "MARKETPLACE"

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    users = relationship("User", back_populates="university")
    locations = relationship("Location", back_populates="university")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    is_admin = Column(Boolean, default=False)

    university = relationship("University", back_populates="users")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)

    university = relationship("University", back_populates="locations")

class DeliveryJob(Base):
    __tablename__ = "delivery_jobs"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    pickup_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    drop_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    source_type = Column(SQLEnum(RequestSourceType), default=RequestSourceType.EXTERNAL_PARCEL)
    tip = Column(Float, default=0.0)
    total_fee = Column(Float, default=10.0)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.AVAILABLE)
    otp_code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    reference_price = Column(Float, nullable=False)
    listing_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    status = Column(SQLEnum(MarketplaceStatus), default=MarketplaceStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    payer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.SIMULATED_UPI)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    is_simulated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ratee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("delivery_jobs.id"), nullable=True)
    score = Column(Integer, nullable=False)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)