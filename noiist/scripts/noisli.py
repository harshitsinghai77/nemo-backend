import asyncio


def dangerously_drop_noistli_table():
    """Drop table from the database."""
    from noiist.config.database import engine
    from noiist.models.noisli import noisli_user

    noisli_user.drop(engine)


async def fake_analytics_data():
    """Fake analytics data for testing."""
    from datetime import datetime, timedelta

    from noiist.config.database import database
    from noiist.models.noisli import noisli_user_analytics

    await database.connect()
    date = datetime.now() - timedelta(days=4)
    user_analytics = {
        "created_at": date,
        "google_id": "105048648072263223821",
        "duration": 20000,
        "full_date": date,
    }

    query = noisli_user_analytics.insert().values(**user_analytics)
    await database.execute(query)
    await database.disconnect()


async def get_analytics():
    from noiist.config.database import database

    await database.connect()
    google_id = "105048648072263223821"
    query = """
        SELECT TO_CHAR(full_date, 'Mon DD') as weekday, SUM(duration) as total_count
        from core_noisli_analytics
        where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
        GROUP BY TO_CHAR(full_date, 'Mon DD')
        ORDER BY full_date
    """

    results = await database.fetch_all(query, values={"google_id": google_id})
    for r in results:
        print(r["weekday"], r["total_count"])
    await database.disconnect()


async def get_stastics():
    from noiist.config.database import database

    await database.connect()
    google_id = "105048648072263223821"
    query = """
        SELECT * from core_noisli_analytics
        where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
        and duration = (SELECT MAX (duration) from core_noisli_analytics)
    """

    results = await database.fetch_one(query, values={"google_id": google_id})
    print({**results})
    await database.disconnect()


loop = asyncio.get_event_loop()
loop.run_until_complete(fake_analytics_data())
loop.close()
