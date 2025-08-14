from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import date
from uuid import uuid4
import os

# Load environment variables from .env file
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(MONGODB_URI)
db = client["certify"]

@app.get("/")
async def read_root():
    return {"message": "Hello, Certify!"}

@app.on_event("startup")
def seed_sample_certificate():
    certificates = db["certificates"]
    if certificates.count_documents({}) == 0:
        certificates.insert_one({
            "credentialId": str(uuid4()),
            "name": "Saman Sliva",
            "course": "Club Member",
            "dateIssued": date.today().isoformat(),
            "issuer": "Mozilla Campus Club SLIIT"
        })

@app.get("/api/certificate/{credentialId}")
async def get_certificate(credentialId: str):
    certificates = db["certificates"]
    cert = certificates.find_one({"credentialId": credentialId})
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    cert["_id"] = str(cert["_id"])  # Convert ObjectId to string if needed
    return cert

# Note: To use the PORT variable, run the server with:
# python -m uvicorn main:app --reload --port %PORT%
# (on Windows CMD; use $PORT for bash)
