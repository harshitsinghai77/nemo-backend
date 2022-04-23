import asyncio
import random
from datetime import datetime, timedelta


def dangerously_drop_noistli_table():
    """Drop table from the database."""
    from api.config.database import engine
    from api.models.nemo import nemo_user

    nemo_user.drop(engine)


async def fake_analytics_data():
    """Fake analytics data for testing."""
    from app.api.config.database import async_session, close_connection, create_table
    from app.api.models.nemo import nemo_user_analytics

    await create_table()
    date = datetime.now()

    for i in range(6):
        date -= timedelta(days=i)
        user_analytics = {
            "created_at": date,
            "google_id": "100258543595566787621",
            "duration": 9000,
            "full_date": date,
        }
        async with async_session as session:
            query = nemo_user_analytics.insert().values(**user_analytics)
            await session.execute(query)
            await session.commit()

    await close_connection()


async def fake_tasks_data():
    from app.api.config.database import close_connection
    from app.api.crud.nemo import NemoTask

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


asyncio.run(fake_tasks_data())
