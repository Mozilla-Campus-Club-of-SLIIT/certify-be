from pydantic import BaseModel, Field
from datetime import date

class Certificate(BaseModel):
    credentialId: str = Field(..., description="Unique credential ID")
    name: str = Field(..., description="Recipient's name")
    course: str = Field(..., description="Course name")
    dateIssued: date = Field(..., description="Date certificate was issued")
    issuer: str = Field(..., description="Certificate issuer")
