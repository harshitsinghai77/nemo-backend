import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Header, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse, Response

# from app.api.core.nemo_stream import (
#     clear_streams_cache,
#     get_stream_by_category,
#     get_stream_by_id,
#     populate_stream_cache,
# )
from app.api.core.nemo_sound import fetch_nemo_sound

# from app.api.emails.send_email import send_email
from app.api.crud.nemodeta import NemoDeta
from app.api.pydantic.nemo import (
    Account,
    Analytics,
    CreateTask,
    GetAnalytics,
    GoogleAuth,
    UserAccount,
    UserSettings,
)
from app.api.routers.constants import (
    COOKIE_AUTHORIZATION_NAME,
    COOKIE_DOMAIN,
    JWT_ACCESS_TOKEN_EXPIRE_DAYS,
)
from app.api.utils.nemo import (
    check_google_user,
    create_access_token,
    create_dict_from_payload,
    get_current_user,
    get_user_payload,
)

LOGGER = logging.getLogger()
nemo_deta_route = APIRouter()


def current_user(x_auth_token: str = Header(None)):
    """Get current user based on x_auth_token"""
    if not x_auth_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="x-auth-token header missing."
        )
    user = get_current_user(x_auth_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found from the token. Invalid x-auth-token.",
        )
    return user


@nemo_deta_route.post("/login")
def create_user(auth: GoogleAuth):
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to validate google user",
        )

    user = NemoDeta.check_user_exists(google_id=payload["sub"])
    # If user does not exists then create new user
    if not user:
        user_obj = create_dict_from_payload(payload)
        user = NemoDeta.create_new_user(user_obj)
        # send welcome email to user as a background task
        # background_tasks.add_task(
        #     send_email,
        #     receiver_fullname=user_obj["given_name"],
        #     receiver_email=user_obj["email"],
        # )

    # create a access token
    access_token_expires = timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"email": user.profile.email, "google_id": user.profile.google_id},
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


@nemo_deta_route.get("/settings")
def get_user_settings(user=Depends(current_user)):
    """Get all user settings."""
    settings = NemoDeta.get_user_settings(user["google_id"])
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No settings found for the user",
        )
    return settings


@nemo_deta_route.patch("/settings")
def update_user_timer_settings(settings: UserSettings, user=Depends(current_user)):
    """Update user settings."""
    updated_setting = settings.dict(exclude_unset=True)
    NemoDeta.update_settings(
        google_id=user["google_id"], updated_setting=updated_setting
    )
    return updated_setting


@nemo_deta_route.get("/user-image")
def get_user_image_url(user=Depends(current_user)):
    """Get user image recieved from google login."""
    user_image_url = NemoDeta.get_user_image_url(google_id=user["google_id"])
    return {"profile_pic": user_image_url}


@nemo_deta_route.get("/account", response_model=UserAccount)
def get_user_account(user=Depends(current_user)):
    """Get user account."""
    account = NemoDeta.get_user_profile(google_id=user["google_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user account found or is empty.",
        )
    return account


@nemo_deta_route.patch("/account", response_model=UserAccount)
def update_user_account(account: Account, user=Depends(current_user)):
    """Update user account."""
    account_dict = account.dict()
    NemoDeta.update_user_account(
        google_id=user["google_id"], updated_profile=account_dict
    )
    return account_dict


@nemo_deta_route.get("/analytics")
def get_user_analytics(user=Depends(current_user)):
    """Get all analytics."""
    analytics = NemoDeta.get_analytics(google_id=user["google_id"])
    return analytics


@nemo_deta_route.post("/analytics", response_model=GetAnalytics)
def create_user_analytics(analytics: Analytics, user=Depends(current_user)):
    """Create new analytics."""
    created_at = datetime.now()
    user_analytics = {
        "created_at": str(created_at),
        "google_id": user["google_id"],
        "duration": analytics.duration,
        "full_date": str(created_at),
    }
    analytics = NemoDeta.create_analytics(user_analytics)
    return analytics


@nemo_deta_route.get("/statistics/{stats}")
def get_stats(user=Depends(current_user), stats=str):
    """Get statistics."""
    user_google_id = user["google_id"]
    if stats == "best-day":
        results = NemoDeta.analytics_get_best_day(google_id=user_google_id)
        return results
    if stats == "current-goal":
        results = NemoDeta.analytics_get_current_goal(google_id=user_google_id)
        return results
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Invalid category or category not found"},
    )


@nemo_deta_route.get("/get-tasks")
def get_tasks(user=Depends(current_user)):
    """Get all task."""
    all_tasks = NemoDeta.get_task_summary(user["google_id"])
    return all_tasks


@nemo_deta_route.post("/create_task")
def create_new_task(task: CreateTask, user=Depends(current_user)):
    """Create new task."""
    task = task.dict()
    task["google_id"] = user["google_id"]
    new_task = NemoDeta.create_new_task(task)
    return new_task


@nemo_deta_route.delete("/tasks/{task_key}")
def delete_task_by_task_id(user=Depends(current_user), task_key=str):
    """Get all task."""
    NemoDeta.delete_task_by_key(key=task_key)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True},
    )


@nemo_deta_route.delete("/delete")
def delete_user(user=Depends(current_user)):
    """Permanently remove user from the database."""
    user_google_id = user["google_id"]
    NemoDeta.completely_remove_user(google_id=user_google_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "google_id": user_google_id},
    )


@nemo_deta_route.get("/cdn/{sound_id}")
async def cdn(sound_id: str):
    """Fetch nemo sound from Deta Drive and return the file as Response."""
    file = fetch_nemo_sound(sound_id)
    if not file:
        raise HTTPException(status_code=404)
    headers = {"Cache-Control": "public, max-age=86400"}
    return Response(
        content=file.read(),
        media_type="application/octet-stream",
        headers=headers,
    )


# @nemo_deta_route.get("/get-streams-by-category/{category}")
# async def nemo_get_stream_by_category(category: str):
#     """Get streams from pafy and return the data."""
#     if category:
#         result = await get_stream_by_category(category=category)
#         return result
#     return JSONResponse(
#         status_code=status.HTTP_204_NO_CONTENT,
#         content={"message": "Category not found"},
#     )


# @nemo_deta_route.get("/get-stream-by-id/{category}/{video_id}")
# async def nemo_get_stream_by_id(category: str, video_id: str):
#     """Fetch streams by id."""
#     if video_id and category:
#         result = get_stream_by_id(category=category, video_id=video_id)
#         return result
#     return JSONResponse(
#         status_code=status.HTTP_204_NO_CONTENT,
#         content={"message": "Category or Id not found"},
#     )


# @nemo_deta_route.get("/clear-stream-cache")
# async def clear_streams():
#     """Clear streams from cache.
#     This should be called when streams url have expired.
#     """
#     clear_streams_cache()
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"message": "Cleared streams cache."},
#     )


# @nemo_deta_route.get("/populate-lofi-stream-cache")
# async def populate_lofi_stream_cache():
#     """Populates Nemo Lofi Stream Cache"""
#     await populate_stream_cache()
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"message": "Succesfully created request."},
#     )
