import os
import requests
from fastapi import HTTPException, Request


def verify_token(token: str) -> dict:
    ACCOUNTS_SERVICE_URI = os.getenv("ACCOUNTS_SERVICE_URI", "https://accounts.sliitmozilla.org")
    response = requests.get(f"{ACCOUNTS_SERVICE_URI}/api/users/me", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    })
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.reason)
    
    return response.json()["data"]
    
def role_required(allowed_roles: list):
    def dependency(request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
        token = auth_header.split(" ")[1]

        user = verify_token(token)
        roles = user.get("roles")
        has_role = False

        for role in roles:
            if role in allowed_roles:
                has_role = True
                break
        if not has_role:
            raise HTTPException(status_code=403, detail="You do not have permission for this endpoint")
        
        return user
    return dependency