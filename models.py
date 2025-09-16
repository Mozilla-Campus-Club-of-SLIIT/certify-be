from pydantic import BaseModel, Field
from datetime import date

class Certificate(BaseModel):
    id: str = Field(..., alias="_id", description="MongoDB ObjectId")
    credentialId: str = Field(..., description="Unique credential ID")
    name: str = Field(..., description="Recipient's name")
    course: str = Field(..., description="Course name")
    categoryCode: str = Field(..., description="Short code for certificate type")
    categoryName: str = Field(..., description="Full name of certificate type")
    dateIssued: date = Field(..., description="Date certificate was issued")
    issuer: str = Field(..., description="Certificate issuer")

    class Config:
        allow_population_by_field_name = True  
