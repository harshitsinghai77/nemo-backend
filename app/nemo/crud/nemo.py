from app.nemo.config.database import database
from app.nemo.models.nemo import nemo_user, nemo_user_analytics, nemo_user_settings


class NemoUser:
    """Utility class to manage nemo user."""

    @staticmethod
    async def create(user_dict):
        """Create a new user."""
        query = nemo_user.insert().values(**user_dict)
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def update(google_id, user_dict):
        """Update existing user."""
        query = (
            nemo_user.update()
            .where(nemo_user.c.google_id == google_id)
            .values(**user_dict)
        )
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def get_user_by_id(google_id: str):
        """Get the user from the database."""
        query = nemo_user.select().where(nemo_user.c.google_id == google_id)
        return await database.fetch_one(query)

    @staticmethod
    async def delete(google_id: str):
        """Delete the user from the database."""
        query = nemo_user.delete().where(nemo_user.c.google_id == google_id)
        return await database.execute(query)

    @staticmethod
    async def completely_remove_user(google_id):
        """Delete user profile, user settings and user analytics as a transaction."""
        async with database:
            async with database.transaction():
                query_user = nemo_user.delete().where(
                    nemo_user.c.google_id == google_id
                )
                query_settings = nemo_user_settings.delete().where(
                    nemo_user_settings.c.google_id == google_id
                )
                query_analytics = nemo_user_analytics.delete().where(
                    nemo_user_analytics.c.google_id == google_id
                )
                await database.execute(query_analytics)
                await database.execute(query_settings)
                await database.execute(query_user)

    @staticmethod
    async def check_if_email_exists(email: str):
        """Check if the email already exists."""
        query = nemo_user.select().where(nemo_user.c.email == email)
        return await database.fetch_one(query)

    @staticmethod
    async def check_user_exists(google_id: str, email: str):
        """Check if user exists."""
        query = nemo_user.select().where(
            nemo_user.c.google_id == google_id and nemo_user.c.email == email
        )
        return await database.fetch_one(query)


class NemoSettings:
    """Utility class to manage nemo user settings."""

    @staticmethod
    async def create(google_id):
        """Create new user settings."""
        query_settings = nemo_user_settings.insert().values({"google_id": google_id})
        return await database.execute(query_settings)

    @staticmethod
    async def get(google_id):
        """Get user settings."""
        query = nemo_user_settings.select().where(
            nemo_user_settings.c.google_id == google_id
        )
        return await database.fetch_one(query)

    @staticmethod
    async def update(google_id, settings_dict):
        """Update user settings."""
        query = (
            nemo_user_settings.update()
            .where(nemo_user_settings.c.google_id == google_id)
            .values(**settings_dict)
        )
        return await database.execute(query)

    @staticmethod
    async def delete(google_id):
        """Delete user settings"""
        query = nemo_user_settings.delete().where(
            nemo_user_settings.c.google_id == google_id
        )
        return await database.execute(query)


class NemoAnalytics:
    """Utility class to manage nemo user analytics."""

    @staticmethod
    async def create(user_analytics):
        """Create new analytic."""
        query = nemo_user_analytics.insert().values(**user_analytics)
        await database.execute(query)
        return user_analytics

    @staticmethod
    async def get(google_id):
        """Get user analytics."""
        query = nemo_user_analytics.select().where(
            nemo_user_analytics.c.google_id == google_id
        )
        return await database.fetch_all(query)

    @staticmethod
    async def get_analytics(google_id):
        """Get Weekly Anlytics."""
        query = """
            SELECT TO_CHAR(full_date, 'Mon DD') as weekday, SUM(duration) as total_count
            from core_nemo_analytics
            where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
            GROUP BY TO_CHAR(full_date, 'Mon DD')
            ORDER BY TO_CHAR(full_date, 'Mon DD')
        """
        results = await database.fetch_all(query, values={"google_id": google_id})
        return results

    @staticmethod
    async def get_best_day(google_id):
        """Return most number of seconds completed in the last 7 days."""
        query = """
            SELECT * from core_nemo_analytics
            where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
            and duration = (SELECT MAX (duration) from core_nemo_analytics)
        """
        results = await database.fetch_one(query, values={"google_id": google_id})
        return results

    @staticmethod
    async def get_current_goal(google_id):
        """Get current number of hours completed in the day."""
        query = """
            SELECT SUM(duration) as current_goal from core_nemo_analytics
            where DATE(full_date) = CURRENT_DATE and google_id=:google_id
        """
        return await database.fetch_one(query, values={"google_id": google_id})

    @staticmethod
    async def delete(google_id):
        """Delete user analytics"""
        query = nemo_user_analytics.delete().where(
            nemo_user_analytics.c.google_id == google_id
        )
        return await database.execute(query)
