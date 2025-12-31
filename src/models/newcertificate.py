from typing import List

from pydantic import BaseModel


class CertificateCreate(BaseModel):
    name: str
    course: str
    categoryCode: str
    categoryName: str
    issuer: str
    signatures: List[str]
