import random
from datetime import datetime, timedelta

import asyncio

from app.api.crud.nemodeta import NemoDeta

google_id = "id-1234"
user = {
    "created_at": str(datetime.utcnow()),
    "google_id": google_id,
    "given_name": "Harshit",
    "family_name": "Shadow77",
    "email": "harshitsinghai767@hello.com",
    "profile_pic": "my_profile_pic",
    "email_verified": True,
}

analytics = {
    "created_at": str(datetime.utcnow()),
    "duration": 4200,
    "full_date": str(datetime.utcnow()),
}



def create_n_task(n):
    for i in range(n):
        date = datetime.now() - timedelta(days=i)
        print('date: ', date)
        task = {
            "created_at": str(date),
            "task_description": f"Task - {i}",
            "duration": random.randint(3600, 14400),
            "task_date": str(date)
        }
        NemoDeta.create_new_task(google_id, task)


def create_n_analytics(n):
    for i in range(n):
        date = datetime.now() - timedelta(days=i)
        print("date: ", date)
        user_analytics = {
            "google_id": google_id,
            "created_at": str(date),
            "duration": random.randint(3600, 14400),
            "full_date": str(date),
        }
        NemoDeta.create_analytics(user_analytics)


async def main():
    NemoDeta().create(user)
    # check_user_exists = NemoDeta().check_user_exists(google_id)
    # user_settings = NemoDeta().get_user_settings(google_id)
    # updated = NemoDeta.update_settings(
    #     google_id=google_id,
    #     updated_setting={
    #         "timer_time": 5200,
    #         "daily_goal": 5,
    #         "timer_web_notification": False,
    #     },
    # )

    updated_profile = NemoDeta.update_user_account(
        google_id=google_id,
        updated_profile={
            "email": "harshitsinghai77@gmail.com"
        },
    )
    # user_img = NemoDeta.get_user_image_url(google_id)
    # user = NemoDeta.get_user_by_id(google_id)
    # create_n_analytics(20)
    # get_total_hrs = NemoDeta.analytics_get_total_hrs(google_id)
    # print('get_total_hrs: ', get_total_hrs)
    # get_best_day = NemoDeta.analytics_get_best_day(google_id)
    # print('get_best_day: ', get_best_day)
    # current_goal = NemoDeta.analytics_get_current_goal(google_id)
    # print('current_goal: ', current_goal)
    
    # create_n_task(20)
    # all_tasks = NemoDeta.get_tasks(google_id)
    # print("all_tasks: ", all_tasks)
    # NemoDeta.delete_task_by_id("08rc3rx5oaxa")
    # print("deleted")
    # await NemoDeta.completely_remove_user(google_id)
    # print("Done")
    # user = NemoDeta.get_settings("my-random-gid-123")
    # print("user: ", user)
    # pass


asyncio.run(main())
