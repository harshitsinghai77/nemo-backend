from datetime import datetime, timedelta
import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

from pydantic import BaseModel
from noiist.routers.constants import (
    JWT_ACCESS_TOKEN_EXPIRE_DAYS,
    COOKIE_AUTHORIZATION_NAME,
    COOKIE_DOMAIN,
)

from noiist.utils.noisli import (
    check_google_user,
    create_dict_from_payload,
    get_user_payload,
    create_access_token,
    get_current_user,
)
from noiist.crud.noisli import NoisliUser, NoisliSettings, NoisliAnalytics

LOGGER = logging.getLogger()
noisli_route = APIRouter()


class GoogleAuth(BaseModel):
    """User google token."""

    google_token: str


class JWToken(BaseModel):
    """Returns JWT token for the user."""

    jwt_token: str


class UserAccount(BaseModel):
    """Return user account."""

    given_name: Optional[str] = None
    family_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    profile_pic: Optional[str] = None


class UserPreferences(BaseModel):
    """Update user UI preference."""

    preference_shuffle_time: str
    preference_background_color: str


class UserAnalytics(BaseModel):
    """User Analytics"""

    created_at: datetime
    google_id: str
    duration: int
    full_date: datetime


@noisli_route.post("/login")
async def create_user(auth: GoogleAuth):
    """Create a new user or return existing user

    Args:
        auth (GoogleAuth): String containing unique JWT Token from google

    Raises:
        HTTPException: [description]

    Returns:
        `string`: JWT Access token
    """
    # Get user payload from auth token
    payload = get_user_payload(token=auth.google_token)
    if not check_google_user(payload):
        raise HTTPException(
            status_code=400, detail="Unable to validate google user")

    user = await NoisliUser.check_user_exists(payload["sub"],
                                              payload["email"])
    # If user does not exists then create new user and settings for the user
    if not user:
        user_obj = create_dict_from_payload(payload)
        user = await NoisliUser.create(user_obj)
        await NoisliSettings.create(google_id=user["google_id"])

    # create a access token
    access_token_expires = timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"email": user["email"], "google_id": user["google_id"]},
        expires_delta=access_token_expires,
    )
    access_token = jsonable_encoder(access_token)

    response = JSONResponse(
        {"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {access_token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )

    return response


@noisli_route.get("/settings")
async def get_user_settings(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")

    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token")
    settings = await NoisliSettings.get(user["google_id"])
    if not settings:
        raise HTTPException(
            status_code=404, detail="No settings found for the user")
    return settings


@noisli_route.patch("/settings")
async def update_user_timer_settings(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")

    user = get_current_user(token)
    updated_body = await request.json()
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token")
    user = await NoisliSettings.update(
        google_id=user["google_id"], settings_dict=updated_body
    )
    return user


@noisli_route.get("/account", response_model=UserAccount)
async def get_user_account(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")

    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token")
    user = await NoisliUser.get(user["google_id"])
    return user


@noisli_route.patch("/account", response_model=UserAccount)
async def update_user_account(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")

    user = get_current_user(token)
    updated_body = await request.json()
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token")
    user = await NoisliUser.update(google_id=user["google_id"],
                                   user_dict=updated_body)
    return user


@noisli_route.get("/analytics")
async def get_user_analytics(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")
    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token")

    results = await NoisliAnalytics.get_analytics(google_id=user["google_id"])
    return results


@noisli_route.post("/analytics", response_model=UserAnalytics)
async def create_user_analytics(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")
    user = get_current_user(token)
    req_body = await request.json()
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token")

    user_date = datetime.now()
    user_analytics = {
        "created_at": user_date,
        "google_id": user['google_id'],
        "duration": req_body['duration'],
        "full_date": user_date,
    }

    analytics = await NoisliAnalytics.create(user_analytics)
    return analytics


@noisli_route.get("/delete")
async def delete_user(request: Request = None):
    token = request.headers.get("x-auth-token")
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect headers")
    user = get_current_user(token)
    user_google_id = user['google_id']
    await NoisliAnalytics.delete(google_id=user_google_id)
    await NoisliSettings.delete(google_id=user_google_id)
    await NoisliUser.delete(google_id=user_google_id)
    return {'success': True, 'google_id': user_google_id}
