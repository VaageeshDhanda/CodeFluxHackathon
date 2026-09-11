from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add this block immediately after app initialization
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, including your Android WebView
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)