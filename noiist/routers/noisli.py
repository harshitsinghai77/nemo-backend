import os
import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests

from noiist.config.database import database
from noiist.models import noisli

LOGGER = logging.getLogger()
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
noisli_route = APIRouter()


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
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            item.google_token,
            requests.Request(),
            CLIENT_ID,
        )

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
