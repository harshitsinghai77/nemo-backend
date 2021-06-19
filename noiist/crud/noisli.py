from pydantic.types import NoneStr
from noiist.config.database import database
from noiist.models.noisli import noisli_user


class NoisliAdmin:
    @staticmethod
    async def create(user_dict):
        query = noisli_user.insert().values(**user_dict)
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def update(user_dict):
        query = noisli_user.update().where(noisli_user.c.id == 7).values(**user_dict)
        last_record = await database.execute(query)
        return {**user_dict, "id": last_record}

    @staticmethod
    async def get(id):
        query = noisli_user.select().where(noisli_user.c.id == id)
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
