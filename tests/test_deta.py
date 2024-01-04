import random
from datetime import datetime, timedelta

import pytest

from app.api.crud.nemodeta import NemoDeta

@pytest.fixture
def google_id():
    google_id = "my_test_id"
    return google_id


@pytest.fixture
def user(google_id):
    user = {
        "created_at": str(datetime.utcnow()),
        "google_id": google_id,
        "given_name": "Kai",
        "family_name": "Havertz",
        "username": "khavertz29",
        "email": "kaihavertz@chelseafc.com",
        "profile_pic": "my_profile_pic",
        "email_verified": True,
    }
    return user


@pytest.fixture
def settings():
    settings = {
        "daily_goal": 4,
        "display_time": "45 : 00",
        "preference_background_color": "rainbow",
        "preference_shuffle_time": 10,
        "timer_auto_start": False,
        "timer_break_end_notification": False,
        "timer_end_notification": False,
        "timer_sessions": 4,
        "timer_show_timer_on_browser_tab": False,
        "timer_time": "2700",
        "timer_web_notification": False,
    }
    return settings


def test_create_user(user):
    new_user = NemoDeta().create_new_user(user)
    assert new_user.profile.dict() == user


def test_check_user_exists(google_id):
    check_user_exists = NemoDeta().check_user_exists(google_id)
    assert check_user_exists


def test_check_invalid_user_exists():
    check_user_exists = NemoDeta().check_user_exists("random#user@77")
    assert not check_user_exists


def test_get_user_settings(settings, google_id):
    user_settings = NemoDeta().get_user_settings(google_id)
    assert user_settings.dict() == settings


def test_update_settings(google_id):
    # Retrieve original setting
    original_setting = NemoDeta().get_user_settings(google_id).dict()
    new_setting = {
        "timer_time": "5200",
        "daily_goal": 10,
        "timer_web_notification": True,
        "preference_background_color": "SomeRandomColor",
    }
    
    NemoDeta.update_settings(
        google_id=google_id,
        updated_setting=new_setting,
    )

    # Retrieve data and check if data has been updated
    user_setting = NemoDeta().get_user_settings(google_id).dict()

    # Locally update original_setting with the new_setting
    original_setting.update(new_setting)
    assert original_setting == user_setting


def test_get_user_profile(google_id, user):
    deta_user_profile = NemoDeta.get_user_profile(google_id)
    deta_user_profile = deta_user_profile.dict()
    deta_user_profile["created_at"] = deta_user_profile["created_at"][:10]

    user["created_at"] = user["created_at"][:10]
    assert deta_user_profile == user


def test_update_user_account(google_id):
    new_email = "something_just_like@kai.com"
    NemoDeta.update_user_account(
        google_id=google_id,
        updated_profile={"email": new_email},
    )
    user_profile = NemoDeta.get_user_profile(google_id)
    user_profile = user_profile.dict()
    assert user_profile["email"] == new_email


def test_get_user_image_url(google_id, user):
    user_img = NemoDeta.get_user_image_url(google_id)
    assert user_img == user["profile_pic"]


def test_get_user_by_id(google_id):
    user = NemoDeta.get_user_by_id(google_id)
    assert user


def test_create_analytics(google_id):
    n = 20
    for i in range(n):
        date = datetime.now() - timedelta(days=i)
        user_analytics = {
            "google_id": google_id,
            "created_at": str(date),
            "duration": random.randint(3600, 14400),
            "full_date": str(date),
        }
        new_analytics = NemoDeta.create_analytics(user_analytics)
        assert new_analytics.dict() == user_analytics


def test_get_total_hours(google_id):
    get_total_hrs = NemoDeta.get_analytics(google_id)
    assert get_total_hrs is not None
    assert len(get_total_hrs) > 1
    assert get_total_hrs == sorted(get_total_hrs, key=lambda x: x["month_number"])
    assert all(key in get_total_hrs[0].keys() for key in ("weekday", "total_count"))


def test_get_best_day(google_id):
    best_day = NemoDeta.analytics_get_best_day(google_id)
    assert best_day is not None
    assert len(best_day) > 1
    assert best_day["full_date"]


def test_get_current_goal(google_id):
    current_goal = NemoDeta.analytics_get_current_goal(google_id)
    assert current_goal is not None
    assert current_goal["current_goal"]


def test_create_task(google_id):
    n = 20
    for i in range(n):
        date = datetime.now() - timedelta(days=i)
        task = {
            "created_at": str(date),
            "google_id": google_id,
            "task_description": f"Task - {i}",
            "duration": random.randint(3600, 14400),
            "task_date": str(date),
        }
        new_task = NemoDeta.create_new_task(task)
        assert new_task == task


def test_get_all_tasks(google_id):
    all_tasks = NemoDeta.get_all_tasks(google_id)
    assert all_tasks
    assert len(all_tasks) > 0

def test_get_task_summary(google_id):
    all_tasks = NemoDeta.get_task_summary(google_id)
    assert all_tasks
    assert len(all_tasks) > 0


def test_completely_remove_user(google_id):
    NemoDeta.completely_remove_user(google_id)


def test_remove_all_user_task(google_id):
    all_tasks = NemoDeta.delete_all_user_task(google_id)

    all_tasks = NemoDeta.get_all_tasks(google_id, filter_task=False)
    assert len(all_tasks) == 0


def test_delete_all_user_analytics(google_id):
    NemoDeta.delete_all_user_analytics(google_id, filter_analytics=False)

    get_total_hrs = NemoDeta.get_analytics(google_id)
    get_best_day = NemoDeta.analytics_get_best_day(google_id)
    get_current_goal = NemoDeta.analytics_get_current_goal(google_id)
    assert get_total_hrs is None
    assert get_best_day is None
    assert get_current_goal is None
