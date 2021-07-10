from noiist.config.database import database
from noiist.models.noisli import noisli_user, noisli_user_settings, noisli_user_analytics


class NoisliUser:
    """Utility class to manage noisli user."""

    @staticmethod
    async def create(user_dict):
        """Create a new user."""
        query = noisli_user.insert().values(**user_dict)
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def update(google_id, user_dict):
        """Update an existing user."""
        query = (
            noisli_user.update()
            .where(noisli_user.c.google_id == google_id)
            .values(**user_dict)
        )
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def get(google_id):
        """Get the user from the database."""
        query = noisli_user.select().where(
            noisli_user.c.google_id == google_id
        )
        return await database.fetch_one(query)

    @staticmethod
    async def delete(google_id: str):
        """Delete the user from the database."""
        query = noisli_user.delete().where(
            noisli_user.c.google_id == google_id
        )
        return await database.fetch_one(query)

    @staticmethod
    async def check_if_email_exists(email: str):
        """Check if the email already exists."""
        query = noisli_user.select().where(noisli_user.c.email == email)
        return await database.fetch_one(query)

    @staticmethod
    async def check_user_exists(google_id: str, email: str):
        """Check if user exists."""
        query = noisli_user.select().where(
            noisli_user.c.google_id == google_id and
            noisli_user.c.email == email
        )
        return await database.fetch_one(query)


class NoisliSettings:
    """Utility class to manage noisli user settings."""

    @staticmethod
    async def create(google_id):
        """Create new user settings."""
        query_settings = noisli_user_settings.insert().values(
            {"google_id": google_id})
        return await database.execute(query_settings)

    @staticmethod
    async def get(google_id):
        """Get user settings."""
        query = noisli_user_settings.select().where(
            noisli_user_settings.c.google_id == google_id
        )
        return await database.fetch_one(query)

    @staticmethod
    async def update(google_id, settings_dict):
        """Update user settings."""
        query = (
            noisli_user_settings.update()
            .where(noisli_user_settings.c.google_id == google_id)
            .values(**settings_dict)
        )
        await database.execute(query)
        return settings_dict


class NoisliAnalytics:
    """Utility class to manage noisli user analytics."""

    @staticmethod
    async def create(user_analytics):
        """Create new analytics."""
        query = noisli_user_analytics.insert().values(**user_analytics)
        await database.execute(query)
        return user_analytics

    @staticmethod
    async def get(google_id):
        """Get user analytics."""
        query = noisli_user_analytics.select().where(
            noisli_user_analytics.c.google_id == google_id
        )
        return await database.fetch_all(query)

    @staticmethod
    async def get_analytics(google_id):
        """Get Weekly Anlytics."""
        query = """
            SELECT TO_CHAR(full_date, 'Mon DD') as weekday, SUM(duration) as total_count
            from core_noisli_analytics
            where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
            GROUP BY TO_CHAR(full_date, 'Mon DD')
        """
        results = await database.fetch_all(query, values={"google_id": google_id})
        return results
