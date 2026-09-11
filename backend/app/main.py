from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import delivery, marketplace, payments, admin, ratings, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="HostleHive API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers including auth
app.include_router(auth.router)
app.include_router(delivery.router)
app.include_router(marketplace.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(ratings.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HostleHive API"}