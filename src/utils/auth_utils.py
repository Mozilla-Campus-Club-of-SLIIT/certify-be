from fastapi import HTTPException, Request
from jose import JWTError, jwt

from src.config import ALGORITHM, SECRET_KEY


def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  
    except JWTError as e:
        print("JWT verification error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")
    
def role_required(allowed_roles: list):
    def dependency(request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
        token = auth_header.split(" ")[1]
        user = verify_jwt(token)
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have permission for this endpoint")
        return user
    return dependency