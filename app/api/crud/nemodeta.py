from datetime import datetime, timedelta
from unittest import result

import aiohttp
import asyncio
import pandas as pd
from typing import Optional, List
from pydantic import BaseModel

from app.api.config.detabase import (
    deta_db,
    deta_task_db,
    deta_analytics_db,
    PROJECT_KEY,
    PROJECT_ID,
    DETA_TASK_BASENAME,
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
    created_at: Optional[str]
    duration: Optional[int]
    full_date: Optional[str]


class NemoTasks(BaseModel):
    created_at: Optional[str]
    google_id: Optional[str]
    task_description: Optional[str]
    duration: Optional[int]
    task_date: Optional[str]


class NemoUser(BaseModel):
    profile: NemoUserInformation
    settings: NemoSettings


# async_db = deta.AsyncBase("nemo")
headers = {"X-API-Key": PROJECT_KEY}


class NemoPandasDataFrame:
    def __init__(self, items_dict: dict):
        self.df = pd.DataFrame(items_dict)
        if self.df.empty:
            return
        self.df['created_at'] = pd.to_datetime(self.df['created_at'])

    def check_empty_dataframe(func): 
        def is_df_empty(self):
            if self.df.empty:
                print("Dataframne is empty")
                return
            return func(self)                 
        return is_df_empty 
    
    @check_empty_dataframe
    def get_total_hours(self):
        self.df['weekday'] = self.df['created_at'].dt.strftime("%b %d")
        self.df = self.df.groupby(by='weekday', as_index=False).sum()
        self.df = self.df.rename({'duration': 'total_count'}, axis=1)  # new method
        return self.df.to_dict(orient='records')

    @check_empty_dataframe
    def get_best_day(self):
        self.df['weekday'] = self.df['created_at'].dt.strftime("%b %d")
        self.df = self.df.groupby(by='weekday').sum()
        maximum_value_index = self.df['duration'].idxmax()
        result = self.df.loc[maximum_value_index]
        return result.to_dict()
    
    @check_empty_dataframe
    def get_current_goal(self):
        current_date = pd.to_datetime("today")
        result = self.df[self.df['created_at'].dt.date == current_date.date()]
        return {"current_goal": result['duration'].sum()}
    
    @check_empty_dataframe
    def all_tasks(self):
        # drop unnecessary columns if exists
        self.df = self.df.drop(['google_id', 'task_date'], axis=1, errors='ignore')
        
        # create date column
        self.df['date'] = self.df['created_at'].dt.strftime("%b %d %Y")
        
        # groupby date column
        df2 = self.df.groupby(by='date').sum()
        df2 = df2.rename({'duration': 'total_duration'}, axis=1)
        
        # join dataframe
        result = self.df.join(df2, on=['date'])
        return result.to_dict(orient='records')


class NemoDeta:
    """Utility class to manage nemo in Deta Base."""

    @staticmethod
    async def delete_task_http(session, key):
        url = (
            f"https://database.deta.sh/v1/{PROJECT_ID}/{DETA_TASK_BASENAME}/items/{key}"
        )
        async with  session.delete(url, headers=headers) as resp:
            print(resp.status)

    @staticmethod
    def create(user_dict) -> NemoUser:
        """Create a new user in deta base."""
        user = NemoUser(
            profile=NemoUserInformation(**user_dict),
            settings=NemoSettings(),
        )
        deta_db.put(user.dict(), key=user_dict["google_id"])
        return user

    @staticmethod
    def check_user_exists(google_id) -> bool:
        """Check new user in the deta base"""
        return deta_db.get(google_id)

    @staticmethod
    def get_user_settings(google_id: str) -> NemoSettings:
        user = deta_db.get(google_id)  # retrieving item with google_id
        if not user:
            return
        settings = NemoSettings(**user)
        return settings

    @staticmethod
    def update_settings(google_id: str, updated_setting) -> None:
        if not updated_setting:
            return
        updated_setting = {f"settings.{k}": v for k, v in updated_setting.items()}
        deta_db.update(updated_setting, key=google_id)

    @staticmethod
    def update_user_account(google_id: str, updated_profile) -> None:
        if not updated_profile:
            return
        updated_profile = {f"profile.{k}": v for k, v in updated_profile.items()}
        deta_db.update(updated_profile, key=google_id)

    @staticmethod
    def get_user_image_url(google_id: str) -> str:
        user = deta_db.get(google_id)
        if not user:
            return
        user = NemoUser(**user)
        return user.profile.profile_pic

    @staticmethod
    def get_user_by_id(google_id: str) -> NemoUser:
        user = deta_db.get(google_id)
        return user

    def get_user_analytics(func):
        def inner(*args):
            google_id = args[0]
            seven_day_interval = datetime.now() - timedelta(days=7)
            query = {
                "google_id": google_id,
                "created_at?gte": str(seven_day_interval),
            }
            res = deta_analytics_db.fetch(query)
            all_analytics = res.items

            # fetch until last is 'None'
            while res.last:
                res = deta_task_db.fetch(last=res.last)
                all_analytics += res.items

            return func(all_analytics)
        return inner

    @get_user_analytics
    def analytics_get_total_hrs(user_analytics):
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
    def create_analytics(analytics: dict) -> NemoAnalytics:
        if not analytics:
            return
        new_analytics = NemoAnalytics(**analytics)
        deta_analytics_db.put(new_analytics.dict())

    @staticmethod
    def get_tasks(google_id: str) -> List[NemoTasks]:
        ten_day_interval = datetime.now() - timedelta(days=10)
        query = {
            "google_id": google_id,
            "created_at?gte": str(ten_day_interval),
        }
        res = deta_task_db.fetch(query)
        user_tasks = res.items

        # fetch until last is 'None'
        while res.last:
            res = deta_task_db.fetch(last=res.last)
            user_tasks += res.items

        dataframe = NemoPandasDataFrame(user_tasks)
        result = dataframe.all_tasks()
        return result

    @staticmethod
    def create_new_task(google_id: str, task: dict) -> NemoTasks:
        if not task:
            return

        task["google_id"] = google_id
        new_task = NemoTasks(**task)
        deta_task_db.put(data=new_task.dict())
        return new_task

    @staticmethod
    def delete_task_by_id(key: str) -> None:
        if not key:
            raise ValueError("No key found.")
        deta_task_db.delete(key=key)

    @classmethod
    async def delete_all_tasks(cls, googl_id: str):
        """Get all the tasks and then make multiple delete request concurrently using asyncio."""
        # at the time of writing, deta doesn't support deleteMany.
        all_tasks = cls.get_tasks(googl_id)
        all_tasks = [task["key"] for task in all_tasks]

        async with aiohttp.ClientSession() as session:
            task = [
                asyncio.ensure_future(cls.delete_task_http(session, key))
                for key in all_tasks
            ]
            await asyncio.gather(*task)
            print("All task deleted")

    @classmethod
    async def completely_remove_user(cls, google_id: str) -> None:
        if not google_id:
            raise ValueError("no google_id found.")

        # delete use info
        deta_db.delete(google_id)
        # delete all tasks associated to user.
        await cls.delete_all_tasks(google_id)
