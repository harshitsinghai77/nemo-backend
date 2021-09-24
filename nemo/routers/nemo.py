import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Header
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse

from nemo.crud.nemo import NemoAnalytics, NemoSettings, NemoUser

# from nemo.emails.send_email import send_email
from nemo.pydantic.nemo import (
    Account,
    Analytics,
    GetAnalytics,
    GoogleAuth,
    UserAccount,
    UserSettings,
)
from nemo.routers.constants import (
    COOKIE_AUTHORIZATION_NAME,
    COOKIE_DOMAIN,
    JWT_ACCESS_TOKEN_EXPIRE_DAYS,
)
from nemo.utils.nemo import (
    check_google_user,
    create_access_token,
    create_dict_from_payload,
    get_current_user,
    get_user_payload,
)

LOGGER = logging.getLogger()
nemo_route = APIRouter()


async def current_user(x_auth_token: str = Header(None)):
    """Get current user based on x_auth_token"""
    if not x_auth_token:
        raise HTTPException(status_code=400, detail="x-auth-token header missing.")
    user = get_current_user(x_auth_token)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No user found from the token. Invalid x-auth-token.",
        )
    return user


@nemo_route.post("/login")
async def create_user(auth: GoogleAuth, background_tasks: BackgroundTasks):
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
        raise HTTPException(status_code=400, detail="Unable to validate google user")

    user = await NemoUser.check_user_exists(payload["sub"], payload["email"])
    # If user does not exists then create new user and settings for the user
    if not user:
        user_obj = create_dict_from_payload(payload)
        user = await NemoUser.create(user_obj)
        await NemoSettings.create(google_id=user["google_id"])
        # send welcome email to user as a background task
        # background_tasks.add_task(
        #     send_email,
        #     receiver_fullname=user_obj["given_name"],
        #     receiver_email=user_obj["email"],
        # )

    # create a access token
    access_token_expires = timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
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


@nemo_route.get("/settings")
async def get_user_settings(user=Depends(current_user)):
    """Get all user settings."""
    settings = await NemoSettings.get(user["google_id"])
    if not settings:
        raise HTTPException(status_code=404, detail="No settings found for the user")
    return settings


@nemo_route.patch("/settings")
async def update_user_timer_settings(
    settings: UserSettings, user=Depends(current_user)
):
    """Update user settings."""
    updated_body = settings.dict(exclude_unset=True)
    user = await NemoSettings.update(
        google_id=user["google_id"], settings_dict=updated_body
    )
    return user


@nemo_route.get("/account", response_model=UserAccount)
async def get_user_account(user=Depends(current_user)):
    """Get user account."""
    user = await NemoUser.get(user["google_id"])
    return user


@nemo_route.patch("/account", response_model=UserAccount)
async def update_user_account(account: Account, user=Depends(current_user)):
    """Update user account."""
    account_dict = account.dict()
    user = await NemoUser.update(google_id=user["google_id"], user_dict=account_dict)
    return user


@nemo_route.get("/analytics")
async def get_user_analytics(user=Depends(current_user)):
    """Get all analytics."""
    results = await NemoAnalytics.get_analytics(google_id=user["google_id"])
    return results


@nemo_route.post("/analytics", response_model=GetAnalytics)
async def create_user_analytics(analytics: Analytics, user=Depends(current_user)):
    """Create new analytics."""
    user_date = datetime.now()
    user_analytics = {
        "created_at": user_date,
        "google_id": user["google_id"],
        "duration": analytics.duration,
        "full_date": user_date,
    }

    analytics = await NemoAnalytics.create(user_analytics)
    return analytics


@nemo_route.get("/statistics")
async def get_stats(user=Depends(current_user)):
    """Get all statistics."""
    user_google_id = user["google_id"]
    results = await NemoAnalytics.get_best_day(google_id=user_google_id)
    return results


@nemo_route.delete("/delete")
async def delete_user(user=Depends(current_user)):
    """Permanently remove user from the database."""
    user_google_id = user["google_id"]
    await NemoAnalytics.completely_remove_user(google_id=user_google_id)
    return {"success": True, "google_id": user_google_id}
