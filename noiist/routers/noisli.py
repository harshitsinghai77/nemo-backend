from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Header, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse

from noiist.pydantic.noisli import (
    GoogleAuth,
    UserAccount,
    GetAnalytics,
    UserSettings,
    Analytics,
    Account
)
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
from noiist.emails.send_email import send_email

LOGGER = logging.getLogger()
noisli_route = APIRouter()


async def current_user(x_auth_token: str = Header(None)):
    if not x_auth_token:
        raise HTTPException(status_code=400, detail="x-auth-token header missing.")
    user = get_current_user(x_auth_token)
    if not user:
        raise HTTPException(
            status_code=404, detail="No user found from the token. Invalid x-auth-token.")
    return user


@noisli_route.post("/login")
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
        raise HTTPException(
            status_code=400, detail="Unable to validate google user")

    user = await NoisliUser.check_user_exists(payload["sub"],
                                              payload["email"])
    # If user does not exists then create new user and settings for the user
    if not user:
        user_obj = create_dict_from_payload(payload)
        user = await NoisliUser.create(user_obj)
        await NoisliSettings.create(google_id=user["google_id"])
        # send welcome email to user with FastAPI background task
        background_tasks.add_task(
            send_email,
            receiver_fullname=user_obj['given_name'],
            receiver_email=user_obj['email']
        )

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
async def get_user_settings(user=Depends(current_user)):
    settings = await NoisliSettings.get(user["google_id"])
    if not settings:
        raise HTTPException(
            status_code=404, detail="No settings found for the user")
    return settings


@noisli_route.patch("/settings")
async def update_user_timer_settings(settings: UserSettings, user=Depends(current_user)):
    updated_body = settings.dict(exclude_unset=True)
    user = await NoisliSettings.update(
        google_id=user["google_id"], settings_dict=updated_body
    )
    return user


@noisli_route.get("/account", response_model=UserAccount)
async def get_user_account(user=Depends(current_user)):
    user = await NoisliUser.get(user["google_id"])
    return user


@noisli_route.patch("/account", response_model=UserAccount)
async def update_user_account(account: Account, user=Depends(current_user)):
    account_dict = account.dict()
    user = await NoisliUser.update(google_id=user["google_id"],
                                   user_dict=account_dict)
    return user


@noisli_route.get("/analytics")
async def get_user_analytics(user=Depends(current_user)):
    results = await NoisliAnalytics.get_analytics(google_id=user["google_id"])
    return results


@noisli_route.post("/analytics", response_model=GetAnalytics)
async def create_user_analytics(analytics: Analytics, user=Depends(current_user)):
    user_date = datetime.now()
    user_analytics = {
        "created_at": user_date,
        "google_id": user['google_id'],
        "duration": analytics.duration,
        "full_date": user_date,
    }

    analytics = await NoisliAnalytics.create(user_analytics)
    return analytics


@noisli_route.get("/statistics")
async def get_stats(user=Depends(current_user)):
    user_google_id = user['google_id']
    results = await NoisliAnalytics.get_best_day(google_id=user_google_id)
    return results


@noisli_route.delete("/delete")
async def delete_user(user=Depends(current_user)):
    user_google_id = user['google_id']
    await NoisliAnalytics.delete(google_id=user_google_id)
    await NoisliSettings.delete(google_id=user_google_id)
    await NoisliUser.delete(google_id=user_google_id)
    return {'success': True, 'google_id': user_google_id}
