from datetime import datetime, timedelta

from sqlalchemy import and_, desc
from sqlalchemy.sql import func

from app.api.config.database import async_engine, async_session
from app.api.models.nemo import (
    nemo_user,
    nemo_user_analytics,
    nemo_user_settings,
    nemo_user_task,
)


class NemoUser:
    """Utility class to manage nemo user."""

    @staticmethod
    async def create(user_dict):
        """Create a new user."""
        async with async_session() as session:
            query = nemo_user.insert().values(**user_dict).returning(nemo_user.c.id)
            last_record = await session.execute(query)
            last_record = last_record.fetchone()
            await session.commit()
            return {**user_dict, "id": last_record.id}

    @staticmethod
    async def update(google_id, user_dict):
        """Update existing user."""
        async with async_session() as session:
            query = (
                nemo_user.update()
                .where(nemo_user.c.google_id == google_id)
                .values(**user_dict)
            )
            await session.execute(query)
            await session.commit()
            return {**user_dict}

    @staticmethod
    async def get_user_by_id(google_id: str):
        """Get the user from the database."""
        async with async_session() as session:
            query = nemo_user.select().where(nemo_user.c.google_id == google_id)
            result = await session.execute(query)
            return result.fetchone()

    @staticmethod
    async def delete(google_id: str):
        """Delete the user from the database."""
        async with async_session() as session:
            query = nemo_user.delete().where(nemo_user.c.google_id == google_id)
            return await session.execute(query)

    @staticmethod
    async def completely_remove_user(google_id):
        """Delete user profile, user settings and user analytics as a transaction."""
        async with async_engine.begin() as conn:
            query_user = nemo_user.delete().where(nemo_user.c.google_id == google_id)
            query_settings = nemo_user_settings.delete().where(
                nemo_user_settings.c.google_id == google_id
            )
            query_analytics = nemo_user_analytics.delete().where(
                nemo_user_analytics.c.google_id == google_id
            )
            await conn.execute(query_analytics)
            await conn.execute(query_settings)
            await conn.execute(query_user)

    @staticmethod
    async def check_if_email_exists(email: str):
        """Check if email already exists."""
        async with async_session() as session:
            query = nemo_user.select().where(nemo_user.c.email == email)
            return await session.fetch_one(query)

    @staticmethod
    async def check_user_exists(google_id: str, email: str):
        """Check if user already exists."""
        async with async_session() as session:
            query = nemo_user.select().where(
                nemo_user.c.google_id == google_id and nemo_user.c.email == email
            )
            result = await session.execute(query)
            return result.fetchone()

    @staticmethod
    async def get_user_profile_pic(google_id: str):
        """Check if user exists."""
        async with async_session() as session:
            query = (
                nemo_user.select()
                .with_only_columns([nemo_user.c.profile_pic])
                .where(nemo_user.c.google_id == google_id)
            )
            result = await session.execute(query)
            return result.fetchone()


class NemoSettings:
    """Utility class to manage nemo user settings."""

    @staticmethod
    async def create(google_id):
        """Create new user settings."""
        async with async_session() as session:
            query_settings = nemo_user_settings.insert().values(
                {"google_id": google_id}
            )
            await session.execute(query_settings)
            return await session.commit()

    @staticmethod
    async def get(google_id):
        """Get user settings."""
        async with async_session() as session:
            query = nemo_user_settings.select().where(
                nemo_user_settings.c.google_id == google_id
            )
            result = await session.execute(query)
            return result.fetchone()

    @staticmethod
    async def update(google_id, settings_dict):
        """Update user settings."""
        async with async_session() as session:
            query = (
                nemo_user_settings.update()
                .where(nemo_user_settings.c.google_id == google_id)
                .values(**settings_dict)
            )
            await session.execute(query)
            return await session.commit()

    @staticmethod
    async def delete(google_id):
        """Delete user settings"""
        async with async_session() as session:
            query = nemo_user_settings.delete().where(
                nemo_user_settings.c.google_id == google_id
            )
            return await session.execute(query)


class NemoAnalytics:
    """Utility class to manage nemo user analytics."""

    @staticmethod
    async def create(user_analytics):
        """Create new analytic."""
        async with async_session() as session:
            query = nemo_user_analytics.insert().values(**user_analytics)
            await session.execute(query)
            await session.commit()
            return user_analytics

    @staticmethod
    async def get_analytics(google_id):
        """Get Weekly Anlytics."""
        # """
        # SELECT TO_CHAR(full_date, 'Mon DD') as weekday, SUM(duration) as total_count
        # from core_nemo_analytics
        # where full_date > CURRENT_DATE - INTERVAL '7 days' and google_id=:google_id
        # GROUP BY TO_CHAR(full_date, 'Mon DD')
        # ORDER BY TO_CHAR(full_date, 'Mon DD')
        # """
        seven_day_interval_before = datetime.now() - timedelta(days=7)
        async with async_session() as session:
            query = (
                nemo_user_analytics.select()
                .with_only_columns(
                    [
                        func.to_char(nemo_user_analytics.c.full_date, "Mon DD").label(
                            "weekday"
                        ),
                        func.sum(nemo_user_analytics.c.duration).label("total_count"),
                    ]
                )
                .where(
                    and_(
                        nemo_user_analytics.c.full_date > seven_day_interval_before,
                        nemo_user_analytics.c.google_id == google_id,
                    )
                )
                .group_by("weekday")
                .order_by("weekday")
            )
            result = await session.execute(query)
            result = result.fetchall()
            return result

    @staticmethod
    async def get_best_day(google_id):
        """Return best day (day with most hrs) in the last 7 days."""
        query = """
            SELECT * from core_nemo_analytics
            where google_id=:google_id and full_date > CURRENT_DATE - INTERVAL '7 days'
            and duration = (SELECT MAX (duration) from core_nemo_analytics)
        """
        # seven_day_interval_before = datetime.now() - timedelta(days=7)
        # max_value = func.max(nemo_user_analytics.c.duration)
        # select_max_value = nemo_user_analytics.select(max_value).with_only_columns(nemo_user_analytics.c.duration).scalar_subquery()
        # query = nemo_user_analytics.select().where(
        #     and_(
        #         nemo_user_analytics.c.google_id == google_id,
        #         nemo_user_analytics.c.full_date > seven_day_interval_before,
        #         nemo_user_analytics.c.duration == select_max_value
        #     )
        # )
        async with async_session() as session:
            result = await session.execute(query, {"google_id": google_id})
            return result.fetchone()

    @staticmethod
    async def get_current_goal(google_id):
        """Get current number of hours completed in the day."""
        # """
        #     SELECT SUM(duration) as current_goal from core_nemo_analytics
        #     where DATE(full_date) = CURRENT_DATE and google_id=:google_id
        # """
        async with async_session() as session:
            query = (
                nemo_user_analytics.select()
                .with_only_columns(
                    [func.sum(nemo_user_analytics.c.duration).label("current_goal")]
                )
                .where(
                    and_(
                        func.date(nemo_user_analytics.c.full_date)
                        == func.current_date(),
                        nemo_user_analytics.c.google_id == google_id,
                    )
                )
            )
            result = await session.execute(query)
            return result.fetchone()

    @staticmethod
    async def delete(google_id):
        """Delete user analytics"""
        async with async_session() as session:
            query = nemo_user_analytics.delete().where(
                nemo_user_analytics.c.google_id == google_id
            )
            return await session.execute(query)


class NemoTask:
    """Utility class to manage user taks."""

    @staticmethod
    async def create(task):
        """Create a new task."""
        async with async_session() as session:
            query = nemo_user_task.insert().values(**task)
            await session.execute(query)
            await session.commit()
            task.pop("google_id", None)
            return task

    @staticmethod
    async def get_all_tasks(google_id):
        """Get all the user tasks."""
        # select created_at, task_description, duration, n1.sum_duration from (
        #     SELECT date(created_at) as created_at_1, sum(duration) as sum_duration from core_nemo_tasks group by created_at_1
        # ) as n1 JOIN core_nemo_tasks as n2 ON date(n2.created_at) = date(n1.created_at_1)
        ten_day_interval = datetime.now() - timedelta(days=10)
        sub_query = (
            nemo_user_task.select()
            .with_only_columns(
                [
                    func.date(nemo_user_task.c.created_at).label("created_at_grouped"),
                    func.sum(nemo_user_task.c.duration).label("total_duration"),
                ]
            )
            .group_by("created_at_grouped")
            .order_by(desc("created_at_grouped"))
        )
        sub_query = sub_query.alias("sub_query")

        query = (
            nemo_user_task.select()
            .with_only_columns(
                [
                    nemo_user_task.c.id,
                    func.to_char(nemo_user_task.c.created_at, "Mon DD YYYY").label(
                        "date"
                    ),
                    nemo_user_task.c.created_at,
                    nemo_user_task.c.task_description,
                    nemo_user_task.c.duration,
                    sub_query.c.total_duration,
                ]
            )
            .where(
                and_(
                    nemo_user_task.c.created_at >= ten_day_interval,
                    nemo_user_task.c.google_id == google_id,
                )
            )
        )

        query = query.join(
            sub_query,
            func.date(nemo_user_task.c.created_at)
            == func.date(sub_query.c.created_at_grouped),
        )
        async with async_session() as session:
            result = await session.execute(query)
            return result.fetchall()

    @staticmethod
    async def remove_task_by_task_id(
        task_id,
        google_id,
    ):
        """Given a task_id and google_id remove the task from core_nemo_tasks"""
        query = nemo_user_task.delete().where(
            and_(
                nemo_user_task.c.id == task_id,
                nemo_user_task.c.google_id == google_id,
            )
        )
        async with async_session() as session:
            await session.execute(query)
            return await session.commit()
