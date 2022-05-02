import asyncio
import random
from datetime import datetime, timedelta

from app.api.crud.nemo import NemoTask, NemoAnalytics
from app.api.config.database import close_connection


def dangerously_drop_noistli_table():
    """Drop table from the database."""
    from api.config.database import engine
    from api.models.nemo import nemo_user

    nemo_user.drop(engine)


async def fake_analytics_data():
    """Fake analytics data for testing."""
    date = datetime.now()

    for i in range(6):
        date -= timedelta(days=i)
        user_analytics = {
            "created_at": date,
            "google_id": "105048648072263223821",
            "duration": random.randint(3600, 14400),
            "full_date": date,
        }
        await NemoAnalytics.create(user_analytics)
    print("initialized dummy analytics data")
    await close_connection()


async def fake_tasks_data():
    google_id = "105048648072263223821"
    today_date = datetime.now()

    for i in range(10):
        today_date -= timedelta(days=i)
        for j in range(10):
            today_date -= timedelta(hours=j)
            task = {
                "created_at": today_date,
                "google_id": google_id,
                "task_description": f"task-{i}-{j}",
                "duration": random.randint(1800, 9000),
                "task_date": today_date.date(),
            }
            await NemoTask.create(task)
    print("initialized dummy task data")
    await close_connection()


async def get_analytics():
    from api.config.database import database

    await database.connect()
    google_id = "105048648072263223821"
    query = """
        SELECT TO_CHAR(full_date, 'Mon DD') as weekday, SUM(duration) as total_count
        from core_nemo_analytics
        where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
        GROUP BY TO_CHAR(full_date, 'Mon DD')
        ORDER BY full_date
    """

    results = await database.fetch_all(query, values={"google_id": google_id})
    for r in results:
        print(r["weekday"], r["total_count"])
    await database.disconnect()


async def get_stastics():
    from api.config.database import database

    await database.connect()
    google_id = "100258543595566787621"
    query = """
        SELECT SUM(duration) from core_nemo_analytics
        where DATE(full_date) = CURRENT_DATE and google_id=:google_id
    """
    results = await database.fetch_one(query, values={"google_id": google_id})
    print({**results})
    await database.disconnect()


asyncio.run(fake_analytics_data())
