import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Header, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

# from app.api.emails.send_email import send_email
from app.api.crud.nemo import NemoDeta
from app.api.models.nemo import NemoSettings, NemoUserInformation
from app.api.pydantic.nemo import (
    Account,
    Analytics,
    CreateTask,
    DictPayload,
    GetAnalytics,
    GoogleAuth,
    User,
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
    handle_integrity_error,
)

LOGGER = logging.getLogger()
nemo_route = APIRouter()

def current_user(x_auth_token: str = Header(None)) -> User:
    """Get current user based on x_auth_token"""
    if not x_auth_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="x-auth-token header missing."
        )
    user = User(**get_current_user(x_auth_token))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found from the token. Invalid x-auth-token.",
        )
    return user

@nemo_route.post("/login")
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

    user: NemoUserInformation = NemoDeta.check_user_exists(google_id=payload["sub"])

    # If user does not exists then create new user
    if not user:
        user_obj: DictPayload = create_dict_from_payload(payload)
        user: NemoUserInformation = NemoDeta.create_new_user(user_obj)
        # send welcome email to the new user
        # send_email(receiver_fullname=user_obj["given_name"], receiver_email=user_obj["email"])

    # create a access token
    access_token_expires = timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"email": user.email, "google_id": user.google_id},
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

@nemo_route.get("/settings", response_model=NemoSettings)
def get_user_settings(user: User = Depends(current_user)):
    """Get all user settings."""
    settings: NemoSettings = NemoDeta.get_user_settings(user.google_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No settings found for the user",
        )
    return settings

@nemo_route.post("/settings")
def update_user_timer_settings(
    settings: UserSettings, user: User = Depends(current_user)
):
    """Update user settings."""
    updated_setting = settings.model_dump(exclude_unset=True)
    try:
        NemoDeta.update_settings(
            google_id=user.google_id, updated_setting=updated_setting
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No settings found for the user",
        )
    return updated_setting

@nemo_route.get("/user-image")
def get_user_image_url(user: User = Depends(current_user)):
    """Get user image recieved from google login."""
    user_image_url = NemoDeta.get_user_image_url(google_id=user.google_id)
    return {"profile_pic": user_image_url}

@nemo_route.get("/account", response_model=NemoUserInformation)
def get_user_account(user: User = Depends(current_user)):
    """Get user account."""
    account: NemoUserInformation = NemoDeta.get_user_profile(google_id=user.google_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user account found or is empty.",
        )
    return account

@nemo_route.post("/account", response_model=UserAccount)
def update_user_account(account: Account, user: User = Depends(current_user)):
    """Update user account."""
    account_dict = account.model_dump(exclude_unset=True)
    try:
        NemoDeta.update_user_account(
            google_id=user.google_id, updated_profile=account_dict
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user account found for the user",
        )
    return account_dict

@nemo_route.get("/analytics")
def get_user_analytics(user: User = Depends(current_user)):
    """Get all analytics."""
    analytics = NemoDeta.get_analytics(google_id=user.google_id)
    return analytics

@nemo_route.post("/analytics", response_model=GetAnalytics)
def create_user_analytics(analytics: Analytics, user: User = Depends(current_user)):
    """Create new analytics."""
    try:
        created_at = datetime.now()
        user_analytics = {
            "created_at": created_at,
            "google_id": user.google_id,
            "duration": analytics.duration,
            "full_date": created_at,
        }
        NemoDeta.insert_analytic(user_analytics)
    except IntegrityError as e:
        handle_integrity_error(e)
    return user_analytics

@nemo_route.get("/statistics/{stats}")
def get_stats(user: User = Depends(current_user), stats=str):
    """Get statistics."""
    user_google_id = user.google_id
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

@nemo_route.get("/get-tasks")
def get_tasks(user: User = Depends(current_user)):
    """Get all task."""
    all_tasks = NemoDeta.get_task_summary(user.google_id)
    return all_tasks

@nemo_route.post("/create_task")
def create_new_task(task: CreateTask, user: User = Depends(current_user)):
    """Create new task."""
    try:
        created_at = datetime.now()
        task_dict = {
            **task.model_dump(),
            "google_id": user.google_id,
            "created_at": created_at,
            "task_date": created_at,
        }
        new_task = NemoDeta.insert_new_task(task_dict)
    except IntegrityError as e:
        handle_integrity_error(e)
    return new_task

@nemo_route.delete("/tasks/{task_key}")
def delete_task_by_task_id(task_key=str, user: User = Depends(current_user)):
    """Delete Task"""
    NemoDeta.delete_task_by_key(google_id=user.google_id, key=task_key)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True},
    )

@nemo_route.delete("/delete")
def delete_user(user: User = Depends(current_user)):
    """Permanently remove user from the database."""
    user_google_id = user.google_id
    NemoDeta.remove_user(google_id=user_google_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "google_id": user_google_id},
    )
