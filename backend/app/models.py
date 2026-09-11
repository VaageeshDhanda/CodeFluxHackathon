from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from .database import Base

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RequestSourceType(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    API = "api"

class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    university_id = Column(Integer, ForeignKey("universities.id"))
    is_admin = Column(Boolean, default=False)

class DeliveryJob(Base):
    __tablename__ = "delivery_jobs"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    pickup_location_id = Column(Integer, ForeignKey("locations.id"))
    dropoff_location_id = Column(Integer, ForeignKey("locations.id"))
    reward = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")

class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="available")