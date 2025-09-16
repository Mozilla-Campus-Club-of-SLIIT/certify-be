from pydantic import BaseModel, Field
from datetime import date
from typing import List

class Signature(BaseModel):
    id: str = Field(..., description="Unique ID of the signature document")
    name: str = Field(..., description="Name of the signer")
    post: str = Field(..., description="Position or designation of the signer")
    image_b64: str = Field(..., description="Base64-encoded signature image")

    class Config:
        orm_mode = True

class Certificate(BaseModel):
    id: str = Field(..., alias="_id", description="MongoDB ObjectId")
    credentialId: str = Field(..., description="Unique credential ID")
    name: str = Field(..., description="Recipient's name")
    course: str = Field(..., description="Course name")
    categoryCode: str = Field(..., description="Short code for certificate type")
    categoryName: str = Field(..., description="Full name of certificate type")
    dateIssued: date = Field(..., description="Date certificate was issued")
    issuer: str = Field(..., description="Certificate issuer")
    signatures: List[Signature] = Field(..., description="List of signature objects")
    
    class Config:
        allow_population_by_field_name = True  