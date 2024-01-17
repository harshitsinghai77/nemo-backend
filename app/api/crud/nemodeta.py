from datetime import datetime, timedelta

import pandas as pd
from typing import List
from pydantic import BaseModel

from app.api.config.detabase import (
    getdetabase,
    getdetadrive,
    DETA_BASE_NEMO,
    DETA_BASE_TASK,
    DETA_BASE_ANALYTICS,
    DETA_BASE_AUDIO_STREAM,
    DETA_DRIVE_NEMO_SOUNDS,
)


class NemoUserInformation(BaseModel):
    created_at: str
    id = int
    google_id: str
    given_name: str
    family_name: str
    username: str = ""
    email: str
    profile_pic: str
    email_verified: bool = False


class NemoSettings(BaseModel):
    timer_time: str = 2700
    display_time: str = "45 : 00"
    timer_end_notification: bool = False
    timer_show_timer_on_browser_tab: bool = False
    timer_web_notification: bool = False
    timer_sessions: int = 4
    timer_auto_start: bool = False
    timer_break_end_notification: bool = False
    preference_shuffle_time: int = 10
    preference_background_color: str = "rainbow"
    daily_goal: int = 4


class NemoAnalytics(BaseModel):
    google_id: str
    created_at: str
    duration: int
    full_date: str


class NemoTasks(BaseModel):
    created_at: str
    google_id: str
    task_description: str
    duration: int
    task_date: str


class NemoUser(BaseModel):
    profile: NemoUserInformation
    settings: NemoSettings


class NemoAudioStreamSchema(BaseModel):
    category: str
    title: str
    author: str
    stream_id: str
    url: str
    expiry: float


class NemoPandasDataFrame:
    def __init__(self, items_dict: dict):
        self.df = pd.DataFrame(items_dict)
        if self.df.empty:
            return
        self.df["created_at"] = pd.to_datetime(self.df["created_at"])

    def check_empty_dataframe(func):
        def is_df_empty(self):
            if self.df.empty:
                return []
            return func(self)

        return is_df_empty

    @check_empty_dataframe
    def get_total_hours(self):
        self.df["weekday"] = self.df["created_at"].dt.strftime("%b %d")

        # This will be used in sort by month_number, we want the results to be sorted by months i.e. 30 Nov -> 1 Dec
        self.df["month_number"] = self.df["created_at"].dt.month
        # do not user groupby("weekday").sum(), we want to only sum `duration` column and keep month_number as it is
        self.df = self.df.groupby(by="weekday", as_index=False).agg(
            {
                "duration": "sum",
                "month_number": "first",
            }
        )
        self.df = self.df.sort_values("month_number", ascending=True)
        self.df = self.df.rename({"duration": "total_count"}, axis=1)  # rename column
        return self.df.to_dict(orient="records")

    @check_empty_dataframe
    def get_best_day(self):
        self.df["full_date"] = self.df["created_at"].dt.strftime("%a, %b %d %Y").rename("weekday")
        result = self.df.groupby(by="full_date", as_index=False)["duration"].sum().sort_values("duration", ascending=False).to_dict("records")[0]
        result = {"best_day_full_date": result.pop("full_date"), "best_day_duration": result.pop("duration")}
        return result
    
    @check_empty_dataframe
    def get_current_goal(self):
        current_date = pd.to_datetime("today")
        result = self.df[self.df["created_at"].dt.date == current_date.date()]
        return {"current_goal": int(result["duration"].sum())}

    @check_empty_dataframe
    def prepare_and_summarize_tasks_by_date(self):
        # Drop unnecessary columns
        self.df.drop(["google_id", "task_date"], axis=1, inplace=True, errors="ignore")

         # Convert created_at to datetime
        self.df["created_at"] = pd.to_datetime(self.df["created_at"], utc=True)

        # Create formatted date column
        self.df["date"] = self.df["created_at"].dt.strftime("%b %d %Y")

        # groupby date and sum the duration of each date
        self.df["total_duration"] = self.df.groupby("date")["duration"].transform("sum")

        # Sort values by date
        result = self.df.sort_values("date", ascending=False)
        return result.to_dict(orient="records")

class NemoDeta:
    """Utility class to manage nemo in Deta Base."""

    def get_nemo_detabase(func):
        def inner(*args, **krwargs):
            deta_db = getdetabase(DETA_BASE_NEMO)
            return func(deta_db, *args, **krwargs)

        return inner

    def get_task_detabase(func):
        def inner(*args, **krwargs):
            deta_task_db = getdetabase(DETA_BASE_TASK)
            return func(deta_task_db, *args, **krwargs)

        return inner

    def get_analytics_detabase(func):
        def inner(*args, **krwargs):
            deta_analytics_db = getdetabase(DETA_BASE_ANALYTICS)
            return func(deta_analytics_db, *args, **krwargs)

        return inner

    @get_analytics_detabase
    def get_user_analytics(deta_analytics_db, func):
        def inner(google_id, filter_analytics=True):
            seven_day_interval = datetime.now() - timedelta(days=7)
            query = {"google_id": google_id}
            if filter_analytics:
                query["created_at?gte"] = str(seven_day_interval)
            res = deta_analytics_db.fetch(query)
            all_analytics = res.items

            # fetch until last is 'None'
            while res.last:
                res = deta_analytics_db.fetch(last=res.last)
                all_analytics += res.items

            return func(all_analytics)

        return inner

    @staticmethod
    @get_nemo_detabase
    def create_new_user(deta_db, user_dict) -> NemoUser:
        """Create a new user in deta base."""
        user = NemoUser(
            profile=NemoUserInformation(**user_dict),
            settings=NemoSettings(),
        )
        deta_db.put(user.dict(), key=user_dict["google_id"])
        return user

    @classmethod
    def check_user_exists(cls, google_id) -> bool:
        """Check is user already exists in the deta base"""
        user = cls.get_user_by_id(google_id)
        if user:
            return NemoUser(
                profile=NemoUserInformation(**user["profile"]),
                settings=NemoSettings(**user["settings"]),
            )

    @classmethod
    def get_user_settings(cls, google_id: str) -> NemoSettings:
        user = cls.get_user_by_id(google_id)
        settings = NemoSettings(**user["settings"])
        return settings

    @classmethod
    def get_user_profile(cls, google_id: str) -> NemoUserInformation:
        user = cls.get_user_by_id(google_id)
        profile = NemoUserInformation(**user["profile"])
        return profile

    @staticmethod
    @get_nemo_detabase
    def update_settings(deta_db, google_id: str, updated_setting) -> None:
        if not updated_setting:
            return
        updated_setting = {f"settings.{k}": v for k, v in updated_setting.items()}
        deta_db.update(updated_setting, key=google_id)

    @staticmethod
    @get_nemo_detabase
    def update_user_account(deta_db, google_id: str, updated_profile) -> None:
        if not updated_profile:
            return
        updated_profile = {f"profile.{k}": v for k, v in updated_profile.items()}
        deta_db.update(updated_profile, key=google_id)

    @classmethod
    def get_user_image_url(cls, google_id: str) -> str:
        user = cls.get_user_by_id(google_id)
        profile = NemoUserInformation(**user["profile"])
        return profile.profile_pic

    @staticmethod
    @get_nemo_detabase
    def get_user_by_id(deta_db, google_id: str) -> NemoUser:
        user = deta_db.get(google_id)
        return user

    @get_user_analytics
    def get_analytics(user_analytics):
        pandas_object = NemoPandasDataFrame(user_analytics)
        result = pandas_object.get_total_hours()
        return result

    @get_user_analytics
    def analytics_get_best_day(user_analytics):
        pandas_object = NemoPandasDataFrame(user_analytics)
        result = pandas_object.get_best_day()
        return result

    @get_user_analytics
    def analytics_get_current_goal(user_analytics):
        pandas_object = NemoPandasDataFrame(user_analytics)
        result = pandas_object.get_current_goal()
        return result

    @staticmethod
    @get_analytics_detabase
    def create_analytics(deta_analytics_db, analytics: dict) -> NemoAnalytics:
        if not analytics:
            return
        new_analytics = NemoAnalytics(**analytics)
        deta_analytics_db.put(new_analytics.dict())
        return new_analytics

    @get_task_detabase
    def get_all_tasks(deta_task_db, google_id: str, filter_task=True) -> List[NemoTasks]:
        ten_day_interval = datetime.now() - timedelta(days=10)

        query = {
            "google_id": google_id,
        }
        if filter_task:
            query["created_at?gte"] = str(ten_day_interval)
        res = deta_task_db.fetch(query)
        user_tasks = res.items

        # fetch until last is 'None'
        while res.last:
            res = deta_task_db.fetch(last=res.last)
            user_tasks += res.items

        return user_tasks

    @classmethod
    def get_task_summary(cls, google_id: str, filter_task=True) -> List[NemoTasks]:
        user_tasks = cls.get_all_tasks(google_id, filter_task=filter_task)
        dataframe = NemoPandasDataFrame(user_tasks)
        result = dataframe.prepare_and_summarize_tasks_by_date()
        return result
    
    @staticmethod
    @get_task_detabase
    def create_new_task(deta_task_db, task: dict) -> NemoTasks:
        if not task:
            return
        new_task = NemoTasks(**task)
        deta_task_db.put(data=new_task.dict())
        return new_task

    @staticmethod
    @get_nemo_detabase
    def delete_user_by_key(deta_analytics_db, key: str) -> None:
        if not key:
            raise ValueError("No key found.")
        deta_analytics_db.delete(key=key)

    @staticmethod
    @get_task_detabase
    def delete_task_by_key(deta_task_db, key: str) -> None:
        if not key:
            raise ValueError("No key found.")
        deta_task_db.delete(key=key)

    @staticmethod
    @get_analytics_detabase
    def delete_analytics_by_key(deta_analytics_db, key: str) -> None:
        if not key:
            raise ValueError("No key found.")
        deta_analytics_db.delete(key=key)

    @classmethod
    def delete_all_user_task(cls, google_id: str):
        """Get all the tasks and then delete them sequentially."""
        all_tasks = cls.get_all_tasks(google_id, filter_task=False)
        task_keys = [task["key"] for task in all_tasks]
        for key in task_keys:
            NemoDeta.delete_task_by_key(key)

    @get_user_analytics
    def delete_all_user_analytics(all_analytics):
        """Get all the analytics and then delete them sequentially."""
        analytics_keys = [analytics["key"] for analytics in all_analytics]
        for key in analytics_keys:
            NemoDeta.delete_analytics_by_key(key)

    @classmethod
    def completely_remove_user(cls, google_id: str) -> None:
        if not google_id:
            raise ValueError("Invalid or no google_id found.")

        # delete all tasks associated with user.
        cls.delete_all_user_task(google_id)

        # delete all analytics associated with user.
        cls.delete_all_user_analytics(google_id)

        # delete user info
        cls.delete_user_by_key(google_id)


class NemoAudioStream:
    """Utility class to manage nemo audio streams in Deta Base."""

    def get_nemo_audio_stream_detabase(func):
        def inner(*args, **krwargs):
            deta_db = getdetabase(DETA_BASE_AUDIO_STREAM)
            return func(deta_db, *args, **krwargs)

        return inner

    @staticmethod
    @get_nemo_audio_stream_detabase
    def get_audio_stream(deta_db, stream_id: str) -> NemoUserInformation:
        """Get audio from nemo_audio_stream using stream_id"""
        stream = deta_db.get(stream_id)
        return stream

    @staticmethod
    @get_nemo_audio_stream_detabase
    def create_new_audio_stream(
        deta_db, stream_dict, expire_in=14400
    ) -> NemoAudioStreamSchema:
        """Create new stream entry in nemo_audio_stream deta base"""
        stream = NemoAudioStreamSchema(**stream_dict)
        deta_db.put(stream.dict(), key=stream.stream_id, expire_in=expire_in)
        return stream

    @staticmethod
    @get_nemo_audio_stream_detabase
    def delete_audio_stream(deta_db, stream_id: str) -> NemoUserInformation:
        """Delete audio stream from nemo_audio_stream using stream_id"""
        deta_db.delete(stream_id)

    @staticmethod
    @get_nemo_audio_stream_detabase
    def get_streams_count_in_detabase(deta_db):
        all_streams = deta_db.fetch()
        return all_streams.count


class NemoSoundDrive:
    """Utility class to manage nemo audio streams in Deta Base."""

    def get_nemo_sound_drive(func):
        def inner(*args, **krwargs):
            drive_storage = getdetadrive(DETA_DRIVE_NEMO_SOUNDS)
            return func(drive_storage, *args, **krwargs)

        return inner

    @staticmethod
    @get_nemo_sound_drive
    def get_file_from_drive(drive_storage, sound_id: str) -> NemoUserInformation:
        """Get nemo sound file using sound_id"""
        return drive_storage.get(sound_id)
