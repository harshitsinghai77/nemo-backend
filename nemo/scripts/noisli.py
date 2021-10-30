import asyncio


def dangerously_drop_noistli_table():
    """Drop table from the database."""
    from nemo.config.database import engine
    from nemo.models.nemo import nemo_user

    nemo_user.drop(engine)


async def fake_analytics_data():
    """Fake analytics data for testing."""
    from datetime import datetime, timedelta

    from nemo.config.database import database
    from nemo.models.nemo import nemo_user_analytics

    await database.connect()
    date = datetime.now() + timedelta(days=1)
    # date = datetime.now()
    user_analytics = {
        "created_at": date,
        "google_id": "100258543595566787621",
        "duration": 9000,
        "full_date": date,
    }

    query = nemo_user_analytics.insert().values(**user_analytics)
    await database.execute(query)
    await database.disconnect()


async def get_analytics():
    from nemo.config.database import database

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
    from nemo.config.database import database

    await database.connect()
    google_id = "100258543595566787621"
    query = """
        SELECT SUM(duration) from core_nemo_analytics
        where DATE(full_date) = CURRENT_DATE and google_id=:google_id
    """
    results = await database.fetch_one(query, values={"google_id": google_id})
    print({**results})
    await database.disconnect()


asyncio.run(get_stastics())
