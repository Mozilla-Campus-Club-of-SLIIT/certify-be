import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from uuid import uuid4
import random
import string
import os
from contextlib import asynccontextmanager
from models import Certificate, Signature

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
PORT = int(os.getenv("PORT", 8000))

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

client = MongoClient(MONGODB_URI)
db = client["certify"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def generate_credential_id() -> str:
    prefix = random.choice(string.ascii_lowercase)
    raw_uuid = str(uuid4()).replace("-", "")
    credential_id = f"{prefix}{raw_uuid}"
    logging.info("Generated credential ID: %s", credential_id)
    return credential_id


def get_certificate_by_credential(credential_id: str) -> dict:
    cert = db["certificates"].find_one({"credentialId": credential_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    cert["_id"] = str(cert["_id"])
    logging.info("Fetched certificate for credential ID: %s", credential_id)
    return cert


def get_signatures_by_ids(signature_ids: list) -> list[dict]:
    signature_docs = list(db["signatures"].find({"id": {"$in": signature_ids}}))
    for sig in signature_docs:
        sig["_id"] = str(sig.get("_id", ""))

    logging.info(
        "Fetched %d signature(s) for IDs: %s",
        len(signature_docs),
        signature_ids
    )

    if len(signature_docs) < len(signature_ids):
        missing = set(signature_ids) - {sig["id"] for sig in signature_docs}
        logging.warning("Signatures not found for IDs: %s", list(missing))

    return signature_docs


def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)
    logging.info("Password verification result: %s", result)
    return result


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.info("JWT created for sub: %s, role: %s", to_encode.get("sub"), to_encode.get("role"))
    return token


def authenticate_user(email: str, password: str):
    logging.info("Authenticating user with email: %s", email)
    user = db["users"].find_one({"email": email})
    if not user:
        logging.warning("Authentication failed: user not found for email: %s", email)
        return None
    if not verify_password(password, user["password"]):
        logging.warning("Authentication failed: invalid password for email: %s", email)
        return None
    logging.info("Authentication successful for email: %s", email)
    return user


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        client.admin.command("ping")
        logging.info("Successfully connected to MongoDB")
    except Exception as e:
        logging.error("MongoDB connection failed: %s", e)

    # Seed signatures if empty
    signatures = db["signatures"]
    if signatures.count_documents({}) == 0:
        with open("test_signature.b64", "r") as f:
            base64_signature_1 = f.read().strip()
        signatures.insert_many([
            {"id": "pmvodpn5", "name": "Amal", "post": "President", "image_b64": base64_signature_1},
            {"id": "szoii2l2", "name": "Kamal", "post": "Secretary", "image_b64": base64_signature_1}
        ])
        logging.info("Inserted sample signatures: %s, %s", "pmvodpn5", "szoii2l2")
    else:
        logging.info("Signatures collection already has data, skipping seed.")

    # Seed certificates if empty
    certificates = db["certificates"]
    if certificates.count_documents({}) == 0:
        cred_id = generate_credential_id()
        certificates.insert_one({
            "credentialId": cred_id,
            "name": "Saman Sliva",
            "course": "Club Member",
            "categoryCode": "LC",
            "categoryName": "Leadership & Contribution",
            "dateIssued": date.today().isoformat(),
            "issuer": "Mozilla Campus Club SLIIT",
            "signatures": ["pmvodpn5", "szoii2l2"]
        })
        logging.info("Inserted sample certificate with credentialId: %s", cred_id)
    else:
        logging.info("Certificates collection already has data, skipping seed.")

    users = db["users"]
    if users.count_documents({}) == 0:
        fake_users = [
            {
                "name": "Admin User",
                "email": "admin@example.com",
                "password": pwd_context.hash("1234"),
                "role": "admin"
            },
            {
                "name": "Regular User",
                "email": "user@example.com",
                "password": pwd_context.hash("1234"),
                "role": "user"
            }
        ]
        users.insert_many(fake_users)
        logging.info("Inserted sample users: admin@example.com, user@example.com")
    else:
        logging.info("Users collection already has data, skipping seed.")

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
    logging.info("Root endpoint '/' was called")
    return {"message": "Hello, Certify!"}
    


@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
    except Exception:
        logging.error("Failed to read JSON body in login request")
        raise HTTPException(status_code=400, detail="Invalid request payload")

    email = data.get("email")
    password = data.get("password")

    logging.info("Login attempt for email: %s", email)

    if not email or not password:
        logging.warning("Login failed: missing email or password for email: %s", email)
        raise HTTPException(status_code=400, detail="Email and password required")

    user = authenticate_user(email, password)
    if not user:
        logging.warning("Login failed: invalid credentials for email: %s", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": user["email"], "role": user["role"]}
    access_token = create_access_token(token_data)

    logging.info("Login successful for email: %s", email)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/certificate/{credentialId}")
async def get_certificate(credentialId: str):
    cert_doc = get_certificate_by_credential(credentialId)
    signatures = get_signatures_by_ids(cert_doc.get("signatures", []))
    cert_doc["signatures"] = signatures
    return Certificate(**cert_doc)


# Note: To use the PORT variable, run the server with:
# python -m uvicorn main:app --reload --port %PORT%
# (on Windows CMD; use $PORT for bash)
