import random
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import Integer, case, cast, column, func
from sqlalchemy.event import listens_for
from sqlmodel import Session, SQLModel, select

from app.api.config.database_sqlite import engine
from app.api.models.nemo import (
    NemoAnalytics,
    NemoSettings,
    NemoTasks,
    NemoUserInformation,
)

SQLModel.metadata.create_all(engine)


def random_word(length):
    characters = [ "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ]
    new_str = ""
    i = 0
    while i < length:
        new_str += random.choice(characters)
        i += 1
    return new_str


def default_payload():
    return {
        "created_at": datetime.now(timezone.utc),
        "google_id": "100258543595566787621",
        "given_name": "John",
        "family_name": "Doe",
        "email": "john_doe@gmail.com",
        "profile_pic": "https://img.a.transfermarkt.technology/portrait/big/131978-1662368517.jpg",
        "email_verified": True,
    }


def create_payload():
    return {
        "created_at": datetime.now(timezone.utc),
        "google_id": random_word(10),
        "given_name": random_word(random.randint(5, 15)),
        "family_name": random_word(random.randint(5, 15)),
        "email": random_word(random.randint(5, 20)) + "@gmail.com",
        "profile_pic": "https://img.a.transfermarkt.technology/portrait/big/131978-1662368517.jpg",
        "email_verified": True,
    }


# This event listener will automatically create a settings entry when a new user is inserted.
@listens_for(NemoUserInformation, "after_insert")
def create_settings(mapper, connection, target: NemoUserInformation):
    # Automatically create the related settings entry
    print(f"==>> target: {target}")
    connection.execute(
        NemoSettings.__table__.insert().values({"google_id": target.google_id})
    )


def create_dummy_users():
    lst = [NemoUserInformation(**default_payload())]
    for _ in range(20):
        payload = create_payload()
        user = NemoUserInformation(**payload)
        print(f"==>> user: {user}")
        lst.append(user)

    with Session(engine) as session:
        session.add_all(lst)
        session.commit()
        print("Added users to the table")


def create_dummy_analytics():
    google_id = default_payload().get("google_id", "google_id_123")
    lst = []
    for _ in range(40):
        analytics = NemoAnalytics(
            google_id=google_id,
            created_at=datetime.now().replace(microsecond=0) + timedelta(days=random.randint(2, 50)),
            duration=random.randint(600, 3600),
            full_date=datetime.now(timezone.utc).date() + timedelta(days=random.randint(0, 10)),
        )
        print(f"==>> analytics: {analytics}")
        lst.append(analytics)

    with Session(engine) as session:
        session.add_all(lst)
        session.commit()
        print("Added analytics to the table")


def create_dummy_tasks():
    google_id = default_payload().get("google_id", "google_id_123")
    lst = []
    for _ in range(20):
        _datetime = datetime.now() + timedelta(days=random.randint(1, 60))
        task = NemoTasks(
            google_id=google_id,
            created_at=_datetime,
            task_description=random_word(random.randint(20, 40)),
            duration=random.randint(600, 3600),
            task_date=_datetime,
        )
        print(f"==>> task: {task}")
        lst.append(task)

    with Session(engine) as session:
        session.add_all(lst)
        session.commit()
        print("Added tasks to the table")


def read_user():
    google_id = default_payload().get("google_id", "google_id_123")
    with Session(engine) as session:
        query = select(NemoUserInformation).where(NemoUserInformation.google_id == google_id)
        res = session.exec(query).one()
        print(f"==>> res: {res}")

def get_seven_days() -> datetime:
    seven_days_ago = datetime.now() - timedelta(days=7)
    return seven_days_ago


def get_total_hours(google_id: str):
    """
    Raw SQL:
        SELECT  concat(month_name, ' ', day_of_date) as weekday,
                sum(duration) as total_count, month_number
        FROM (
                SELECT
                    CASE
                        CAST (strftime('%m', date(created_at)) as INT)
                        WHEN 1 THEN 'January'
                        WHEN 2 THEN 'February'
                        WHEN 3 THEN 'March'
                        WHEN 4 THEN 'April'
                        WHEN 5 THEN 'May'
                        WHEN 6 THEN 'June'
                        WHEN 7 THEN 'July'
                        WHEN 8 THEN 'August'
                        WHEN 9 THEN 'September'
                        WHEN 10 THEN 'October'
                        WHEN 11 THEN 'November'
                        ELSE 'December' END as month_name,
                    strftime('%m', date(created_at)) as month_number,
                    strftime('%d', date(created_at)) as day_of_date,
                    duration
                FROM nemo_analytics
                where date(created_at) >= DATE('now', '-7 days')
        )
        group by weekday
        order by weekday
    """
    seven_days_ago = get_seven_days()
    print(f"==>> seven_days_ago: {seven_days_ago}")
    with Session(engine) as session:
        subquery = (
            select(
                NemoAnalytics.duration,
                cast(func.strftime("%m", NemoAnalytics.created_at), Integer).label(
                    "month_number"
                ),
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
            func.concat(
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
                ),
                " ",
                subquery.c.day_of_date,
            ).label("month_name"),
        ).subquery()

        subquery3 = (
            select(
                subquery2.c.month_name,
                func.sum(subquery2.c.duration).label("total_count"),
                subquery2.c.month_number,
            )
            .group_by(subquery2.c.month_name)
            .order_by(subquery2.c.month_name)
        )

        rows: List[NemoAnalytics] = session.exec(subquery3).fetchall()
        # print(f"==>> rows: {rows}")
        for r in rows:
            print(r)


def analytics_get_best_day(google_id):
    seven_days_ago = get_seven_days()
    print(f"==>> seven_days_ago: {seven_days_ago}")
    # SELECT
    #     SUM(duration) as duration,
    #     date(created_at) as my_full_date
    # FROM nemo_analytics
    # where date(created_at) >= DATE('now', '-7 days')
    # group by my_full_date
    # order by duration DESC
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

        row = session.exec(query).fetchone()

    if not row:
        return
    result = {
        "best_day_full_date": datetime.strptime(row.grouped_date, "%Y-%m-%d").strftime("%a, %b %d %Y"),
        "best_day_duration": row.duration,
    }
    return result


def get_current_goal(google_id: str):
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


def get_all_tasks(google_id: str):
    """
    SELECT
        date(created_at),
        duration,
        task_description,
        SUM(duration) OVER (PARTITION by date(created_at)) as total_duration
    FROM
        nemo_tasks
    where date(created_at) >= date('now', '-10 day')
    ORDER BY
        duration DESC;
    """
    ten_day_interval = datetime.now() - timedelta(days=10)
    with Session(engine) as session:
        query = (
            select(
                func.date(NemoTasks.created_at).label("created_at"),
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
        lsts = list(
            map(
                lambda x: {
                    **x._asdict(),
                    "date": datetime.strptime(x.created_at, "%Y-%m-%d").strftime(
                        "%b %d %Y"
                    ),
                },
                rows,
            )
        )
        return lsts


def delete_task_by_key(key: str) -> None:
    with Session(engine) as session:
        statement = select(NemoTasks).where(NemoTasks.id == key)
        task = session.exec(statement).one()

        session.delete(task)
        session.commit()

        print(f"==>> Deleted task: {task}")


# create_dummy_users()
create_dummy_analytics()
create_dummy_tasks()
# read_user()
# print(get_total_hours("google_id_123"))
# print(get_all_tasks("google_id_123"))
# print(delete_task_by_key("91"))
