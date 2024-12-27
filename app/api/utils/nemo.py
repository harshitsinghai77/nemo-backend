import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.exceptions import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.exc import IntegrityError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.api.pydantic.nemo import DictPayload
from app.api.routers.constants import GOOGLE_CLIENT_ID

credentials_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
)

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "09d25e094faa6ca")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

def check_google_user(payload):
    """Check if payload is valid."""
    if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        return False
    if not (payload["email"] and payload["email_verified"]):
        return False
    return True

def create_dict_from_payload(payload) -> DictPayload:
    """Create and return dict from the payload."""
    return {
        "created_at": datetime.now(timezone.utc),
        "google_id": payload["sub"],
        "given_name": payload["given_name"],
        "family_name": payload["family_name"],
        "email": payload["email"],
        "profile_pic": payload["picture"],
        "email_verified": payload["email_verified"],
    }

def get_user_payload(token):
    """Verify oauth2_token and decode user."""
    try:
        decoded = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )
        return decoded
    except ValueError:
        raise credentials_exception

def get_current_user(token):
    """Get the curren user based on token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        return payload
    except jwt.PyJWTError:
        raise credentials_exception

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """Create new access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_date_x_days_ago(x: int) -> datetime:
    seven_days_ago = datetime.now() - timedelta(days=x)
    return seven_days_ago

def handle_integrity_error(e: IntegrityError):
    if "FOREIGN KEY constraint failed" in str(e):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User does not exist.",
        )
    raise HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail="An error occurred while creating the task.",
    )
