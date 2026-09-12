from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .routers import delivery, marketplace, payments, admin, ratings, auth
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="HostleHive API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)
from .database import engine
from . import models

@app.on_event("startup")
def startup_event():
    # WARNING: This temporarily drops the delivery_jobs table to force recreation with new columns.
    # Remove this block after your next successful deploy so you don't lose data in the future!
    models.DeliveryJob.__table__.drop(bind=engine, checkfirst=True)
    models.Base.metadata.create_all(bind=engine)
    
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        uni = db.query(models.University).filter_by(id=1).first()
        if not uni:
            uni = models.University(id=1, name="Lovely Professional University")
            db.add(uni)
            db.commit()

        loc = db.query(models.Location).filter_by(id=1).first()
        if not loc:
            locs = [
                models.Location(id=1, name="Delivery Office 4", university_id=1),
                models.Location(id=2, name="Delivery Office 7", university_id=1),
                models.Location(id=3, name="Hostel 12", university_id=1),
                models.Location(id=4, name="Hostel 4", university_id=1)
            ]
            db.add_all(locs)
            db.commit()

        admin = db.query(models.User).filter_by(email="admin@lpu.in").first()
        if not admin:
            admin_user = models.User(
                name="System Admin",
                email="admin@lpu.in",
                password="adminpassword123",
                university_id=1,
                is_admin=True
            )
            student_user = models.User(
                name="Rahul Sharma",
                email="rahul@lpu.in",
                password="studentpassword123",
                university_id=1,
                is_admin=False
            )
            db.add_all([admin_user, student_user])
            db.commit()
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(delivery.router)
app.include_router(marketplace.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(ratings.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HostleHive API"}