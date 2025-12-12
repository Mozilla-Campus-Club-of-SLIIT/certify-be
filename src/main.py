from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from src.config import PORT
from src.models import Certificate
from src.utils import (
    setup_logging,
    setup_db,
    get_certificate_by_credential,
    get_certificates_by_member,
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

from src.utils.certificate_img_utils import generate_certificate_image

@app.get("/api/certificate/{credential_id}")
async def get_certificate(credential_id: str):
    logger.info(credential_id)
    cert_doc = get_certificate_by_credential(credential_id)
    if not cert_doc:
        raise HTTPException(status_code=404, detail="Certificate not found")

    signatures = get_signatures_by_ids(cert_doc.get("signatures", []))
    cert_doc["signatures"] = signatures

    cert = Certificate(**cert_doc)
    img_b64 = generate_certificate_image(cert)

    # Return all certificate fields plus image_b64
    cert_dict = cert.dict(by_alias=True)
    cert_dict["image_b64"] = img_b64
    return cert_dict


@app.get("/api/member/{member_name}/achievements")
async def get_member_achievements(member_name: str):
    """Get all certificates/achievements for a member by name.
    
    Args:
        member_name: The name of the member (URL encoded if contains spaces).
        
    Returns:
        List of achievements with certificate details and generated images.
    """
    logger.info("Fetching achievements for member: %s", member_name)
    
    certificates = get_certificates_by_member(member_name)
    
    if not certificates:
        raise HTTPException(
            status_code=404,
            detail=f"No achievements found for member: {member_name}"
        )
    
    achievements = []
    for cert_doc in certificates:
        # Fetch signatures for each certificate
        signatures = get_signatures_by_ids(cert_doc.get("signatures", []))
        cert_doc["signatures"] = signatures
        
        cert = Certificate(**cert_doc)
        img_b64 = generate_certificate_image(cert)
        
        cert_dict = cert.dict(by_alias=True)
        cert_dict["image_b64"] = img_b64
        achievements.append(cert_dict)
    
    logger.info("Found %d achievement(s) for member: %s", len(achievements), member_name)
    
    return {
        "member": member_name,
        "total_achievements": len(achievements),
        "achievements": achievements
    }


# Note: To use the PORT variable, run the server with:
# python -m uvicorn src.main:app --reload --port %PORT%
# (on Windows CMD; use $PORT for bash)
