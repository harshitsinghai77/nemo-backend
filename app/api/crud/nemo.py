from datetime import datetime
from typing import List, Dict, Optional

from sqlalchemy import Integer, case, cast, column, func
from sqlalchemy.event import listens_for
from sqlmodel import Session, delete, select

from app.api.config.database_sqlite import engine
from app.api.models.nemo import (
    NemoAnalytics,
    NemoSettings,
    NemoTasks,
    NemoUserInformation,
)
from app.api.utils.nemo import get_date_x_days_ago

class NemoDeta:
    """Utility class to manage nemo in Deta Base."""

    # This event listener will automatically create a NemoSettings entry when a new user is inserted in NemoUserInformation table.
    @listens_for(NemoUserInformation, "after_insert")
    def create_settings_and_user(mapper, connection, target: NemoUserInformation):
        # Automatically create the related settings entry
        connection.execute(
            NemoSettings.__table__.insert().values({"google_id": target.google_id})
        )

    @staticmethod
    def create_new_user(user_dict) -> NemoUserInformation:
        """Create a new user in the NemoUserInformation table."""
        user = NemoUserInformation(**user_dict)
        with Session(engine) as session:
            # this will automatically trigger an event when a new user is inserted in the table.
            # check `@listens_for(NemoUserInformation, "after_insert")`
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(google_id: str) -> NemoUserInformation:
        with Session(engine) as session:
            statement = select(NemoUserInformation).where(NemoUserInformation.google_id == google_id)
            user = session.exec(statement).first()
        return user
    
    @classmethod
    def check_user_exists(cls, google_id) -> NemoUserInformation:
        """Check if user already exists in the NemoUserInformation table"""
        user: NemoUserInformation = cls.get_user_by_id(google_id)
        return user
    
    @staticmethod
    def get_user_settings(google_id: str) -> NemoSettings:
        with Session(engine) as session:
            statement = select(NemoSettings).where(NemoSettings.google_id == google_id)
            user_settings = session.exec(statement).first()
        return user_settings

    @classmethod
    def get_user_profile(cls, google_id: str) -> NemoUserInformation:
        user: NemoUserInformation = cls.get_user_by_id(google_id)
        return user

    @staticmethod
    def update_settings(google_id: str, updated_setting: dict) -> None:
        if not updated_setting:
            return

        with Session(engine) as session:
            statement = select(NemoSettings).where(NemoSettings.google_id == google_id)
            settings = session.exec(statement).one()

            for key, value in updated_setting.items():
                setattr(settings, key, value)

            session.add(settings)
            session.commit()

    @staticmethod
    def update_user_account(google_id: str, updated_profile: dict) -> None:
        if not updated_profile:
            return

        with Session(engine) as session:
            statement = select(NemoUserInformation).where(NemoUserInformation.google_id == google_id)
            user = session.exec(statement).one()

            for key, value in updated_profile.items():
                setattr(user, key, value)

            session.add(user)
            session.commit()

    @staticmethod
    def get_user_image_url(google_id: str) -> str:
        with Session(engine) as session:
            statement = select(NemoUserInformation.profile_pic).where(NemoUserInformation.google_id == google_id)
            profile_pic = session.exec(statement).first()
        return profile_pic


    @staticmethod
    def get_analytics(google_id: str) -> List[NemoAnalytics]:
        seven_days_ago = get_date_x_days_ago(7)
        with Session(engine) as session:
            subquery = (
                select(
                    NemoAnalytics.duration,
                    cast(func.strftime("%m", NemoAnalytics.created_at), Integer).label("month_number"),
                    func.strftime("%d", NemoAnalytics.created_at).label("day_of_date"),
                )
                .where(NemoAnalytics.google_id == google_id)
                .where(NemoAnalytics.created_at >= seven_days_ago)
                .subquery()
            )

            subquery2 = select(
                subquery.c.month_number,
                subquery.c.day_of_date,
                subquery.c.duration,
                (
                    case(
                        (subquery.c.month_number == 1, "January"),
                        (subquery.c.month_number == 2, "February"),
                        (subquery.c.month_number == 3, "March"),
                        (subquery.c.month_number == 4, "April"),
                        (subquery.c.month_number == 5, "May"),
                        (subquery.c.month_number == 6, "June"),
                        (subquery.c.month_number == 7, "July"),
                        (subquery.c.month_number == 8, "August"),
                        (subquery.c.month_number == 9, "September"),
                        (subquery.c.month_number == 10, "October"),
                        (subquery.c.month_number == 11, "November"),
                        (subquery.c.month_number == 12, "December"),
                        else_="Unknown",  # Default case for invalid months
                    ) +
                    " " +
                    subquery.c.day_of_date
                ).label("weekday"),
            ).subquery()

            subquery3 = (
                select(
                    subquery2.c.weekday,
                    func.sum(subquery2.c.duration).label("total_count"),
                    subquery2.c.month_number,
                )
                .group_by(subquery2.c.weekday)
                .order_by(subquery2.c.weekday)
            )

            rows: List[NemoAnalytics] = session.exec(subquery3).fetchall()

        result = list(map(lambda x: x._asdict(), rows))
        return result

    @staticmethod
    def analytics_get_best_day(google_id: str) -> Optional[Dict[str, str]]:
        seven_days_ago = get_date_x_days_ago(7)
        with Session(engine) as session:
            query = (
                select(
                    func.sum(NemoAnalytics.duration).label("duration"),
                    func.date(NemoAnalytics.created_at).label("grouped_date"),
                )
                .where(NemoAnalytics.google_id == google_id)
                .where(NemoAnalytics.created_at >= seven_days_ago)
                .group_by(column("grouped_date"))
                .order_by(column("duration").desc())
                .limit(1)
            )

            row = session.exec(query).first()

        if not row:
            return
        
        result = {
            "best_day_full_date": datetime.strptime(row.grouped_date, "%Y-%m-%d").strftime("%a, %b %d %Y"),
            "best_day_duration": row.duration,
        }
        return result

    @staticmethod
    def analytics_get_current_goal(google_id: str) -> Optional[Dict[str, int]]:
        with Session(engine) as session:
            query = (
                select(func.sum(NemoAnalytics.duration))
                .where(NemoAnalytics.google_id == google_id)
                .where(func.date(NemoAnalytics.created_at) == func.date("now"))
            )
            row = session.exec(query).first()
        if not row:
            return
        return {"current_goal": int(row)}

    @staticmethod
    def insert_analytic(analytics: dict) -> None:
        if not analytics:
            return
        new_analytics = NemoAnalytics(**analytics)
        with Session(engine) as session:
            session.add(new_analytics)
            session.commit()

    @staticmethod
    def get_task_summary(google_id: str) -> List[NemoTasks]:
        ten_day_interval = get_date_x_days_ago(10)
        with Session(engine) as session:
            query = (
                select(
                    NemoTasks.id,
                    NemoTasks.created_at,
                    NemoTasks.duration,
                    NemoTasks.task_description,
                    func.sum(NemoTasks.duration)
                        .over(partition_by=func.date(NemoTasks.created_at))
                        .label("total_duration"),
                )
                .where(NemoTasks.google_id == google_id)
                .where(NemoTasks.created_at >= ten_day_interval)
                .order_by(NemoTasks.duration.desc())
            )

            rows = session.exec(query).fetchall()

        lsts = list(map(lambda x: { **x._asdict(), "date": x.created_at.strftime("%b %d %Y")}, rows))
        return lsts

    @staticmethod
    def insert_new_task(task: dict) -> None:
        if not task: return
        new_task = NemoTasks(**task)
        with Session(engine) as session:
            session.add(new_task)
            session.commit()

    @staticmethod
    def delete_task_by_key(google_id: str, key: str) -> None:
        if not key:
            raise ValueError("No key found.")

        with Session(engine) as session:
            statement = select(NemoTasks).where(NemoTasks.google_id == google_id).where(NemoTasks.id == key)
            task = session.exec(statement).one()

            session.delete(task)
            session.commit()

    @classmethod
    def remove_user(cls, google_id: str) -> None:
        if not google_id:
            raise ValueError("Invalid or no google_id found.")

        with Session(engine) as session:
            statement_user = delete(NemoUserInformation).where(NemoUserInformation.google_id == google_id)
            statement_settings = delete(NemoSettings).where(NemoSettings.google_id == google_id)
            statement_analytics = delete(NemoAnalytics).where(NemoAnalytics.google_id == google_id)
            statement_tasks = delete(NemoTasks).where(NemoTasks.google_id == google_id)

            try:
                session.exec(statement_analytics)
                session.exec(statement_tasks)
                session.exec(statement_settings)
                session.exec(statement_user)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error: {e}")
                raise e
