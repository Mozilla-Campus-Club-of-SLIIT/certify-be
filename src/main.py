from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from src.config import PORT
from src.models import Certificate
from src.utils import (
    setup_logging,
    setup_db,
    get_certificate_by_credential,
    get_signatures_by_ids,
    lifespan
)
from src.utils import (
    authenticate_user,
    create_access_token,
    process_login_request
)


logger = setup_logging(__name__)
db,client = setup_db()
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
    logger.info("Root endpoint '/' was called")
    return {"message": "Hello, Certify!"}
    
@app.post("/api/login")
async def login(request: Request):
    return await process_login_request(request)

@app.get("/api/certificate/{credentialId}")
async def get_certificate(credentialId: str):
    cert_doc = get_certificate_by_credential(credentialId)
    signatures = get_signatures_by_ids(cert_doc.get("signatures", []))
    cert_doc["signatures"] = signatures
    return Certificate(**cert_doc)


# Note: To use the PORT variable, run the server with:
# python -m uvicorn src.main:app --reload --port %PORT%
# (on Windows CMD; use $PORT for bash)
