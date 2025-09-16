from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import date
from uuid import uuid4
import random
import string
import os
from contextlib import asynccontextmanager
from models import Certificate, Signature

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
PORT = int(os.getenv("PORT", 8000))

client = MongoClient(MONGODB_URI)
db = client["certify"]

def generate_credential_id() -> str:
    prefix = random.choice(string.ascii_lowercase)
    raw_uuid = str(uuid4()).replace("-", "")
    return f"{prefix}{raw_uuid}"


def get_certificate_by_credential(credential_id: str) -> dict:
    cert = db["certificates"].find_one({"credentialId": credential_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    cert["_id"] = str(cert["_id"])
    return cert


def get_signatures_by_ids(signature_ids: list) -> list[dict]:
    signature_docs = list(db["signatures"].find({"id": {"$in": signature_ids}}))
    for sig in signature_docs:
        sig["_id"] = str(sig.get("_id", ""))
    return signature_docs


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        client.admin.command("ping")
        print("Successfully connected to MongoDB")
    except Exception as e:
        print("MongoDB connection failed:", e)

    # Seed signatures if empty
    signatures = db["signatures"]
    if signatures.count_documents({}) == 0:
        with open("test_signature.b64", "r") as f:
            base64_signature_1 = f.read().strip()
        signatures.insert_many([
            {"id": "pmvodpn5", "name": "Amal", "post": "President", "image_b64": base64_signature_1},
            {"id": "szoii2l2", "name": "Kamal", "post": "Secretary", "image_b64": base64_signature_1}
        ])
        print("Sample signatures inserted.")

    # Seed certificates if empty
    certificates = db["certificates"]
    if certificates.count_documents({}) == 0:
        certificates.insert_one({
            "credentialId": generate_credential_id(),
            "name": "Saman Sliva",
            "course": "Club Member",
            "categoryCode": "LC",
            "categoryName": "Leadership & Contribution",
            "dateIssued": date.today().isoformat(),
            "issuer": "Mozilla Campus Club SLIIT",
            "signatures": ["pmvodpn5", "szoii2l2"]
        })
    yield


app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello, Certify!"}


@app.get("/api/certificate/{credentialId}")
async def get_certificate(credentialId: str):
    cert_doc = get_certificate_by_credential(credentialId)
    signatures = get_signatures_by_ids(cert_doc.get("signatures", []))
    cert_doc["signatures"] = signatures
    return Certificate(**cert_doc)


# Note: To use the PORT variable, run the server with:
# python -m uvicorn main:app --reload --port %PORT%
# (on Windows CMD; use $PORT for bash)
