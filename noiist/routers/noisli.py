from datetime import timedelta
import logging

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

from pydantic import BaseModel

from noiist.config.database import database
from noiist.models.noisli import noisli_user_settings
from noiist.routers.constants import (
    JWT_ACCESS_TOKEN_EXPIRE_DAYS,
    COOKIE_AUTHORIZATION_NAME,
    COOKIE_DOMAIN,
)

from noiist.utils.noisliy import (
    check_google_user,
    create_dict_from_payload,
    get_user_payload,
    create_access_token,
)
from noiist.crud.noisli import NoisliAdmin, NoisliSettingsAdmin

LOGGER = logging.getLogger()
noisli_route = APIRouter()


class GoogleAuth(BaseModel):
    google_token: str


class JWToken(BaseModel):
    jwt_token: str


@noisli_route.post("/login")
async def get_google_auth(auth: GoogleAuth):
    payload = get_user_payload(token=auth.google_token)

    # query = noisli_user_settings.delete()
    # await database.execute(query)
    # await NoisliAdmin.delete(payload["sub"])

    if not check_google_user(payload):
        raise HTTPException(status_code=400, detail="Unable to validate google user")

    user = await NoisliAdmin.check_user_exists(payload["sub"], payload["email"])

    # If user does not exists then create a new user and new settings for the user
    if not user:
        user_obj = create_dict_from_payload(payload)
        user = await NoisliAdmin.create(user_obj)
        await NoisliSettingsAdmin.create(user_id=user["id"])

    # create a access token
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"email": user["email"], "google_id": user["google_id"]},
        expires_delta=access_token_expires,
    )
    access_token = jsonable_encoder(access_token)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {access_token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )

    return response


@noisli_route.get("/get-details")
async def get_user_details(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")

    # user = get_user_payload(token)
    settings = await NoisliAdmin.get_user_settings()
    return {**settings}
