from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from src.models import Certificate, CertificateBulkImportCreate, CertificateCreate
from src.utils import (
    add_certificate,
    add_certificates_bulk,
    get_certificate_by_credential,
    get_certificates_by_import_id,
    get_signatures_by_ids,
    lifespan,
    role_required,
    setup_db,
    setup_logging,
)
from src.utils.certificate_img_utils import generate_certificate_image

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
    cert_dict = cert.model_dump(by_alias=True)
    cert_dict["image_b64"] = img_b64
    return cert_dict

@app.post("/api/certificate/new")
async def create_certificate(
    payload: CertificateCreate,
    user=Depends(role_required(["Subcommittee", "Admin"]))
):
    cert = add_certificate(payload.model_dump())

    return JSONResponse(
        status_code=201,
        content={
            "message": "Certificate created successfully",
            "certificate": cert
        }
    )


@app.post("/api/certificate/import")
async def import_certificates_bulk(
    payload: CertificateBulkImportCreate,
    user=Depends(role_required(["Subcommittee", "Admin"]))
):
    import_result = add_certificates_bulk(payload.model_dump())

    return JSONResponse(
        status_code=201,
        content={
            "message": "Certificates imported successfully",
            "importId": import_result["importId"],
            "count": import_result["count"],
        },
    )


@app.get("/api/certificate/import/{import_id}")
async def get_certificates_by_import(import_id: str):
    certificates = get_certificates_by_import_id(import_id)
    if not certificates:
        raise HTTPException(status_code=404, detail="Import not found")

    return {
        "importId": import_id,
        "count": len(certificates),
        "certificates": certificates,
    }

# Note: To use the PORT variable, run the server with:
# python -m uvicorn src.main:app --reload --port %PORT%
# (on Windows CMD; use $PORT for bash)