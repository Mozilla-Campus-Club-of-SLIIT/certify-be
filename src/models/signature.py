from pydantic import BaseModel, Field

class Signature(BaseModel):
    id: str = Field(..., description="Unique ID of the signature document")
    name: str = Field(..., description="Name of the signer")
    post: str = Field(..., description="Position or designation of the signer")
    image_b64: str = Field(..., description="Base64-encoded signature image")

    class Config:
        orm_mode = True
