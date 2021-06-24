from sqlalchemy.sql.expression import select
from noiist.config.database import database
from noiist.models.noisli import noisli_user, noisli_user_settings


class NoisliAdmin:
    @staticmethod
    async def create(user_dict):
        query = noisli_user.insert().values(**user_dict)
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def update(google_id, user_dict):
        query = (
            noisli_user.update()
            .where(noisli_user.c.google_id == google_id)
            .values(**user_dict)
        )
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def get(google_id):
        query = noisli_user.select().where(noisli_user.c.google_id == google_id)
        return await database.fetch_one(query)

    @staticmethod
    async def delete(google_id: str):
        query = noisli_user.delete().where(noisli_user.c.google_id == google_id)
        return await database.fetch_one(query)

    @staticmethod
    async def check_if_email_exists(email: str):
        query = noisli_user.select().where(noisli_user.c.email == email)
        return await database.fetch_one(query)

    @staticmethod
    async def check_user_exists(google_id: str, email: str):
        query = noisli_user.select().where(
            noisli_user.c.google_id == google_id and noisli_user.c.email == email
        )
        return await database.fetch_one(query)

    @staticmethod
    async def get_user_settings():
        join = noisli_user.join(
            noisli_user_settings, noisli_user.c.id == noisli_user_settings.c.user_id
        )
        stmt = select([noisli_user_settings]).select_from(join)
        return await database.fetch_one(stmt)


class NoisliSettingsAdmin:
    @staticmethod
    async def create(google_id):
        query_settings = noisli_user_settings.insert().values({"google_id": google_id})
        return await database.execute(query_settings)

    @staticmethod
    async def get(google_id):
        query = noisli_user_settings.select().where(
            noisli_user_settings.c.google_id == google_id
        )
        return await database.fetch_one(query)

    @staticmethod
    async def update(google_id, settings_dict):
        query = (
            noisli_user_settings.update()
            .where(noisli_user_settings.c.google_id == google_id)
            .values(**settings_dict)
        )
        return await database.execute(query)
