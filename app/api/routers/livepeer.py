import os

import httpx
from fastapi import APIRouter, HTTPException
from api.pydantic.livepeer import LivepeerStream

livepeer_route = APIRouter()

LIVEPEER_BASE_URL = "https://livepeer.com/api/"
LIVEPEER_API_KEY = os.getenv("LIVEPEER_API")

streamProfiles = [
    {
        "name": "720p",
        "bitrate": 2000000,
        "fps": 30,
        "width": 1280,
        "height": 720,
    },
    {
        "name": "480p",
        "bitrate": 1000000,
        "fps": 30,
        "width": 854,
        "height": 480,
    },
    {
        "name": "360p",
        "bitrate": 500000,
        "fps": 30,
        "width": 640,
        "height": 360,
    },
]

HEADERS = {
    "content-type": "application/json",
    "authorization": f"Bearer {LIVEPEER_API_KEY}",
}


@livepeer_route.post("/create-new-stream")
async def create_new_stream(stream: LivepeerStream):
    stream_name = stream.stream_name
    if not stream_name:
        raise HTTPException(status_code=400, detail="No stream_name found.")

    json_body = {"name": stream_name, "profiles": streamProfiles}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            LIVEPEER_BASE_URL + "/stream", json=json_body, headers=HEADERS
        )
        print("resp", resp)
        # if resp.status_code == 201:
        #     resp = resp.json()
        #     stream_id = resp["id"]
        #     playbackId = resp["playbackId"]
        #     streamKey = resp["streamKey"]
        #     return {
        #         "stream_id": stream_id,
        #         "playbackId": playbackId,
        #         "streamKey": streamKey,
        #     }
        return resp.json()


@livepeer_route.get("/")
async def get_stream_status(stream_id: str):
    if not stream_id:
        raise HTTPException(status_code=400, detail="No stream_id found.")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{LIVEPEER_BASE_URL}/stream/{stream_id}", headers=HEADERS
        )
        if resp:
            resp = resp.json()
            return resp
        return "Some error occured. Please try again later."
