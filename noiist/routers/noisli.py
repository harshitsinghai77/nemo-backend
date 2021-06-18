import os
import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

import jwt
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from noiist.config.database import database
from noiist.models import noisli
from noiist.routers.constants import CERT_STR

LOGGER = logging.getLogger()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
noisli_route = APIRouter()

# Specify the CLIENT_ID of the app that accesses the backend:
cert_obj = load_pem_x509_certificate(CERT_STR, default_backend())
public_key = cert_obj.public_key()


class Item(BaseModel):
    google_token: str


async def check_if_email_exists(email: str):
    query = noisli.noisli_user.select().where(noisli.noisli_user.c.email == email)
    return await database.fetch_one(query)


async def create_new_user(user_dict):
    query = noisli.noisli_user.insert().values(**user_dict)
    last_record = await database.execute(query)
    return {**user_dict, "id": last_record}


@noisli_route.post("/login")
async def get_access_token_and_refresh_token(item: Item):
    try:
        idinfo = jwt.decode(
            item.google_token, public_key, algorithms="RS256", audience=GOOGLE_CLIENT_ID
        )
        print(idinfo)
        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        print("idinfo", idinfo)
        userid = idinfo["sub"]
        print("userid", userid)
    except ValueError:
        # Invalid token
        pass

    return HTMLResponse(content="<h1>Hello World</h1>", status_code=200)
