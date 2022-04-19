import base64
import datetime
import logging
import os
from typing import Optional

import requests
from api.config.database import database
from api.models import model
from api.routers.constants import (
    GRANT_TYPE,
    REDIRECT_URI,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_TOKEN_URL,
    SPOTIFY_USER_URL,
)
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

LOGGER = logging.getLogger()

spotify_auth = APIRouter()
NOIIST_FRONTEND_URL = os.getenv("NOIIST_FRONTEND_URL")

auth_str = "{}:{}".format(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": "Basic {}".format(b64_auth_str),
}
error_html_content = """<h1>Some Error Occured. Please try again later.</h1>"""
session = requests.Session()


def get_user_information(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    try:
        r = session.get(url=SPOTIFY_USER_URL, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        LOGGER.error("Request error while `get_user_information` %s", e)


def get_access_and_refresh_token(code: str):
    # Get Access and Refresh Token

    request_body = {
        "grant_type": GRANT_TYPE,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    r = session.post(url=SPOTIFY_TOKEN_URL, data=request_body, headers=headers)
    return r.json()


async def check_if_email_exists(email: str):
    query = model.user.select().where(model.user.c.email == email)
    return await database.fetch_one(query)


async def create_new_user(user_dict):
    query = model.user.insert().values(**user_dict)
    last_record = await database.execute(query)
    return {**user_dict, "id": last_record}


@spotify_auth.get("/")
async def get_access_token_and_refresh_token(code: Optional[str] = None):
    if code:
        try:
            resp_token = get_access_and_refresh_token(code=code)
            access_token = resp_token["access_token"]
            refresh_token = resp_token["refresh_token"]

            # Get user information using access token
            user_info = get_user_information(access_token)
            user_email = user_info["email"]

            # Check if user already exists
            check_user = await check_if_email_exists(email=user_email)
            if check_user:
                name = check_user["display_name"]
                already_exists = True
            else:
                user_data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "display_name": user_info["display_name"],
                    "email": user_email,
                    "spotify_url": user_info["external_urls"]["spotify"],
                    "created_at": datetime.datetime.now(),
                }
                new_user = await create_new_user(user_data)
                name = new_user["display_name"]
                already_exists = False

            # Redirect to frontend with information to display
            url = f"{NOIIST_FRONTEND_URL}/authorization-success?name={name}&already_exists={already_exists}"  # noqa: E501
            return RedirectResponse(url=url)

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error occured %s", e)
            return HTMLResponse(content=error_html_content, status_code=200)

    return HTMLResponse(content=error_html_content, status_code=200)
