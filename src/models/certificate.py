from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from .signature import Signature


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

    @field_validator("dateIssued", mode="before")
    def parse_date_issued(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v.strip(), "%Y-%m-%d").date()
        return v

    class Config:
        populate_by_name = True
