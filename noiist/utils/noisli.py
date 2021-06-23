import os
from datetime import datetime, timedelta

import jwt
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from noiist.routers.constants import CERT_STR, GOOGLE_CLIENT_ID

# Specify the CLIENT_ID of the app that accesses the backend:
cert_obj = load_pem_x509_certificate(CERT_STR, default_backend())
public_key = cert_obj.public_key()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
credentials_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def check_google_user(payload):
    """A method which return True if all checks are passed."""
    if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        return False
    if not (payload["email"] and payload["email_verified"]):
        return False
    return True


def create_dict_from_payload(payload):
    """Returns a dict from the payload."""
    return {
        "created_at": datetime.utcnow(),
        "google_id": payload["sub"],
        "given_name": payload["given_name"],
        "family_name": payload["family_name"],
        "email": payload["email"],
        "profile_pic": payload["picture"],
        "email_verified": payload["email_verified"],
    }


def get_user_payload(token):
    try:
        payload = jwt.decode(
            token, public_key, audience=GOOGLE_CLIENT_ID, algorithms="RS256"
        )
        return payload
    except jwt.PyJWTError:
        raise credentials_exception


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
