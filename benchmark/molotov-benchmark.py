import molotov


@molotov.scenario(100)
async def scenario_post(session):
    async with session.get("http://localhost:8000") as resp:
        assert resp.status == 200
