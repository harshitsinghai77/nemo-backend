import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import cache, partial

import pafy
import youtube_dl

with open("app/nemo/data/streams.json") as json_file:
    streams = json.load(json_file)

last_cache_updated = datetime.now()
CACHE_TTL = 19800  # Cache TTL in sec


@cache
def pafy_worker(category: str, video_id: str):
    """Return a stream url given a category and video_id."""
    video_url = f"http://www.youtube.com/watch?v={video_id}"
    video = pafy.new(video_url, basic=False, gdata=False, size=False)
    best_audio = video.getbestaudio()
    if best_audio:
        playurl = best_audio.url
        return {
            "category": category,
            "title": video._title,
            "author": video._author,
            "id": video.videoid,
            "duration": video.duration,
            "url": playurl,
            "expiry": video.expiry,
        }


def check_cache_expiry():
    """Check if cache is expired. By default 5.5 hrs."""
    current_time = datetime.now()
    diff = current_time - last_cache_updated
    return diff.total_seconds() >= CACHE_TTL


def update_cache_time():
    """Set last_cache_updated to current time."""
    global last_cache_updated
    last_cache_updated = datetime.now()


def update_cache():
    """Clear chache, for each category loop through all the video_url and update cache."""
    clear_streams_cache()
    for k in streams.keys():
        video_urls = streams[k]
        max_workers = 10
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            some_func = partial(pafy_worker, k)
            executor.map(some_func, video_urls)
    update_cache_time()


def get_all_streams(category):
    """Get all streams corresponding to a category."""
    if category not in streams.keys():
        return {
            "message": "Invalid category: {}. Should be one of {}".format(
                category, list(streams.keys())
            )
        }

    video_urls = streams[category]
    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        some_func = partial(pafy_worker, category)
        result = list(executor.map(some_func, video_urls))

    return result


def get_stream_by_id(category: str, id: str):
    """Get Any stream by id."""
    return pafy_worker(category=category, video_id=id)


def clear_streams_cache():
    "Clear function cache and remove Youtube DL cache."
    pafy_worker.cache_clear()
    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.cache.remove()


update_cache()
