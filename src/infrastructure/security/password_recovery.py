import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt, JWTError

SECRET_KEY = os.getenv("JWT_RECOVERY_SECRET_KEY", "recovery-secret-key-for-development")
ALGORITHM = "HS256"
RECOVERY_TOKEN_EXPIRE_MINUTES = 15

def create_recovery_token(email: str) -> str:
    expires_delta = timedelta(minutes=RECOVERY_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "recovery"
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_recovery_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "recovery":
            return None
        return payload.get("sub")
    except JWTError:
        return None
