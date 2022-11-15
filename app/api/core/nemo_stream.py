import json
import time
from concurrent.futures import ThreadPoolExecutor

import youtube_dl
import asyncio
import aiohttp

from app.api.core.audio_stream import YoutubeDLWrapper
from app.api.crud.nemodeta import NemoAudioStream


with open("app/api/data/streams.json") as json_file:
    STREAMS = json.load(json_file)

VIDEO_LIFESPAN = 60 * 60 * 5  # 5 hours
CACHE_TTL = 16200  # Cache TTL in sec (4.5 hours)


YOUTUBE_DDL = YoutubeDLWrapper()


def get_streams(video_ids):
    """Process streams using multithreading."""
    if not (video_ids and isinstance(video_ids, list)):
        raise ValueError("Invalid or empty videos_id")

    max_worker = 10
    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        result = list(executor.map(YOUTUBE_DDL.process_stream, video_ids))
    return result


def get_stream_by_category(category):
    """Get all streams corresponding to a category."""
    if category not in STREAMS.keys():
        return {
            "message": "Invalid category: {}. Should be one of {}".format(
                category, list(STREAMS.keys())
            )
        }

    video_urls = STREAMS[category]
    video_urls = [(category, url) for url in video_urls]
    result = get_streams(video_urls)
    return result


def get_stream_by_id(category: str, video_id: str):
    """Get Any stream by id."""
    return YOUTUBE_DDL.process_stream((category, video_id))


def clear_streams_cache():
    "Delete all entries in nemo_audio_stream detabase and remove Youtube DL cache."
    all_stream_id = [video_id for k in STREAMS.keys() for video_id in STREAMS[k]]

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(NemoAudioStream.delete_audio_stream, all_stream_id)

    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.cache.remove()


def get_all_streams_tuple():
    """Generator containing tuple of all the streams."""
    all_stream = ((k, video_id) for k in STREAMS.keys() for video_id in STREAMS[k])
    return all_stream


async def fire_and_forget(video_info, client):
    """Create request to Deta. Don't wait for the response, fire and forget.
    This is used to submit the request for processing and excape the Deta Micros 10s timeout."""

    category, video_id = video_info
    url = f"https://nemo.deta.dev/nemo/get-stream-by-id/{category}/{video_id}"
    await client.get(url)
    await client.close()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


def populate_stream_cache():
    """For each tuple, create a fire and forget request"""
    for chunk in divide_chunks(list(get_all_streams_tuple()), 10):
        for video_info in chunk:
            client = aiohttp.ClientSession()
            asyncio.create_task(fire_and_forget(video_info, client))
        time.sleep(1)
