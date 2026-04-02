from typing import List

from pydantic import BaseModel, Field, field_validator


class BulkImportUser(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)

    @field_validator("name", "email")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


class CertificateBulkImportCreate(BaseModel):
    users: List[BulkImportUser] = Field(..., min_length=1, max_length=100)
    course: str = Field(..., min_length=1)
    categoryCode: str = Field(..., min_length=1)
    categoryName: str = Field(..., min_length=1)
    issuer: str = Field(..., min_length=1)
    signatures: List[str] = Field(..., min_length=1)

    @field_validator("course", "categoryCode", "categoryName", "issuer")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("signatures")
    @classmethod
    def validate_signatures(cls, value: List[str]) -> List[str]:
        cleaned = []
        for signature_id in value:
            if not isinstance(signature_id, str) or not signature_id.strip():
                raise ValueError("Each signature must be a non-empty string")
            cleaned.append(signature_id.strip())
        return cleaned
