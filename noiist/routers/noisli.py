import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

import jwt
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from noiist.utils.noisliy import check_google_user, create_db_user_from_dict
from noiist.crud.noisli import NoisliAdmin
from noiist.routers.constants import CERT_STR, GOOGLE_CLIENT_ID

LOGGER = logging.getLogger()
noisli_route = APIRouter()

# Specify the CLIENT_ID of the app that accesses the backend:
cert_obj = load_pem_x509_certificate(CERT_STR, default_backend())
public_key = cert_obj.public_key()


class GoogleAuth(BaseModel):
    google_token: str


@noisli_route.post("/login")
async def get_google_auth(auth: GoogleAuth):
    try:
        user_info = jwt.decode(
            auth.google_token, public_key, audience=GOOGLE_CLIENT_ID, algorithms="RS256"
        )

        if not check_google_user(user_info):
            print("Prolbme in user_info")
            return

        user_exists = await NoisliAdmin.check_user_exists(
            user_info["sub"], user_info["email"]
        )
        if user_exists:
            return

        user_obj = create_db_user_from_dict(user_info)
        db_user = await NoisliAdmin.create(user_obj)
        
    except jwt.exceptions.InvalidAudienceError:
        LOGGER.exception("jwt.exceptions.InvalidAudienceError: Invalid audience")
    except ValueError:
        # Invalid token
        pass

    return HTMLResponse(content="<h1>Hello World</h1>", status_code=200)
