import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Header, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse

# from app.api.core.get_stream import (
#     check_cache_expiry,
#     clear_streams_cache,
#     get_all_streams,
#     get_stream_by_id,
#     update_cache,
# )
# from app.api.emails.send_email import send_email
from app.api.crud.nemo import NemoAnalytics, NemoSettings, NemoTask, NemoUser
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
nemo_route = APIRouter()


async def current_user(x_auth_token: str = Header(None)):
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to validate google user",
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No settings found for the user",
        )
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


@nemo_route.get("/user-image")
async def get_user_image_url(user=Depends(current_user)):
    """Get user image recieved from google login."""
    user_image_url = await NemoUser.get_user_profile_pic(google_id=user["google_id"])
    return user_image_url


@nemo_route.get("/account", response_model=UserAccount)
async def get_user_account(user=Depends(current_user)):
    """Get user account."""
    account = await NemoUser.get_user_by_id(google_id=user["google_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user account found or is empty.",
        )
    return account


@nemo_route.patch("/account", response_model=UserAccount)
async def update_user_account(account: Account, user=Depends(current_user)):
    """Update user account."""
    account_dict = account.dict()
    user = await NemoUser.update(google_id=user["google_id"], user_dict=account_dict)
    return user


@nemo_route.get("/analytics")
async def get_user_analytics(user=Depends(current_user)):
    """Get all analytics."""
    analytics = await NemoAnalytics.get_analytics(google_id=user["google_id"])
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user analytics found or is empty.",
        )
    return analytics


@nemo_route.post("/analytics", response_model=GetAnalytics)
async def create_user_analytics(analytics: Analytics, user=Depends(current_user)):
    """Create new analytics."""
    created_at = datetime.now()
    user_analytics = {
        "created_at": created_at,
        "google_id": user["google_id"],
        "duration": analytics.duration,
        "full_date": created_at,
    }

    analytics = await NemoAnalytics.create(user_analytics)
    return analytics


@nemo_route.get("/statistics/{stats}")
async def get_stats(user=Depends(current_user), stats=str):
    """Get statistics."""
    user_google_id = user["google_id"]
    if stats == "best-day":
        results = await NemoAnalytics.get_best_day(google_id=user_google_id)
        return results
    if stats == "current-goal":
        results = await NemoAnalytics.get_current_goal(google_id=user_google_id)
        return results
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Invalid category or category not found"},
    )


@nemo_route.get("/get-tasks")
async def get_tasks(user=Depends(current_user)):
    """Get all task."""
    all_tasks = await NemoTask.get_all_tasks(user["google_id"])
    return all_tasks


@nemo_route.post("/create_task")
async def create_new_task(task: CreateTask, user=Depends(current_user)):
    """Create new task."""
    task = task.dict()
    created_at = datetime.fromtimestamp(task["created_at"] / 1000.0)
    task["created_at"] = created_at
    task["google_id"] = user["google_id"]
    task["task_date"] = created_at.date()
    new_task = await NemoTask.create(task)
    return new_task


@nemo_route.delete("/tasks/{task_id}")
async def delete_task_by_task_id(user=Depends(current_user), task_id=int):
    """Get all task."""
    await NemoTask.remove_task_by_task_id(
        task_id=int(task_id), google_id=user["google_id"]
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True},
    )


@nemo_route.delete("/delete")
async def delete_user(user=Depends(current_user)):
    """Permanently remove user from the database."""
    user_google_id = user["google_id"]
    await NemoUser.completely_remove_user(google_id=user_google_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "google_id": user_google_id},
    )


# @nemo_route.get("/get-all-streams/{category}")
# async def get_all_stream(category: str, background_tasks: BackgroundTasks):
#     """Get streams from pafy and return the data."""
#     if category:
#         result = get_all_streams(category=category)
#         if check_cache_expiry():
#             background_tasks.add_task(update_cache)
#         return result
#     return JSONResponse(
#         status_code=status.HTTP_204_NO_CONTENT,
#         content={"message": "Category not found"},
#     )


# @nemo_route.get("/get-stream-by-id/{category}/{id}")
# async def get_stream(category: str, id: str):
#     """Fetch streams by id."""
#     if id and category:
#         result = get_stream_by_id(category=category, id=id)
#         return result
#     return JSONResponse(
#         status_code=status.HTTP_204_NO_CONTENT,
#         content={"message": "Category or Id not found"},
#     )


# @nemo_route.get("/clear-streams")
# async def clear_streams():
#     """Clear streams from cache.
#     This should be called when streams url have expired.
#     """
#     clear_streams_cache()
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"message": "Cleared streams cache."},
#     )
