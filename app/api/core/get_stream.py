import json
from concurrent.futures import ThreadPoolExecutor

import youtube_dl

from app.api.core.audio_stream import YoutubeDDL
from app.api.crud.nemodeta import NemoAudioStream


with open("app/api/data/streams.json") as json_file:
    STREAMS = json.load(json_file)

VIDEO_LIFESPAN = 60 * 60 * 5  # 5 hours
CACHE_TTL = 16200  # Cache TTL in sec (4.5 hours)


YOUTUBE_DDL = YoutubeDDL()


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
