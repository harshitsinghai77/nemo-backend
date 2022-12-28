import json
from concurrent.futures import ThreadPoolExecutor

import youtube_dl
import asyncio
import aiohttp

from app.api.core.audio_stream import YoutubeDLWrapper
from app.api.crud.nemodeta import NemoAudioStream
from app.api.routers.constants import NEMO_BACKEND_URL

with open("app/api/data/streams.json") as json_file:
    STREAMS = json.load(json_file)

VIDEO_LIFESPAN = 60 * 60 * 5  # 5 hours
CACHE_TTL = 16200  # Cache TTL in sec (4.5 hours)


YOUTUBE_DDL = YoutubeDLWrapper()


async def make_get_stream_by_id_request(session, url):
    async with session.get(url) as resp:
        stream = await resp.json()
        return stream


async def get_streams(video_ids):
    """Process streams using multithreading."""
    if not (video_ids and isinstance(video_ids, list)):
        raise ValueError("Invalid or empty videos_id")

    # max_worker = 8
    # with ThreadPoolExecutor(max_workers=max_worker) as executor:
    #     result = list(executor.map(YOUTUBE_DDL.process_stream, video_ids))
    # # result = [YOUTUBE_DDL.process_stream(video_info) for video_info in video_ids]
    # return result
    async with aiohttp.ClientSession() as session:
        tasks = []
        for category, video_id in video_ids:
            stream_url = NEMO_BACKEND_URL + f"/get-stream-by-id/{category}/{video_id}"
            tasks.append(
                asyncio.create_task(
                    make_get_stream_by_id_request(session=session, url=stream_url)
                )
            )

        all_streams = await asyncio.gather(*tasks)

    return all_streams


def get_stream_by_id(category: str, video_id: str):
    """Get Any stream by id."""
    return YOUTUBE_DDL.process_stream((category, video_id))


async def get_stream_by_category(category):
    """Get all streams corresponding to a category."""
    if category not in STREAMS.keys():
        return {
            "message": "Invalid category: {}. Should be one of {}".format(
                category, list(STREAMS.keys())
            )
        }

    video_urls = STREAMS[category]
    video_urls = [(category, url) for url in video_urls]
    result = await get_streams(video_urls)
    result = list(filter(lambda x: x is not None, result))
    return result


def clear_streams_cache():
    "Delete all entries in nemo_audio_stream detabase and remove Youtube DL cache."
    all_stream_id = [video_id for k in STREAMS.keys() for video_id in STREAMS[k]]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(NemoAudioStream.delete_audio_stream, all_stream_id)

    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.cache.remove()


def get_all_streams_tuple():
    """Generator containing tuple of all the streams."""
    all_stream = ((k, video_id) for k in STREAMS.keys() for video_id in STREAMS[k])
    return all_stream


async def populate_stream_cache():
    """For each stream"""
    for category in STREAMS.keys():
        await get_stream_by_category(category)
