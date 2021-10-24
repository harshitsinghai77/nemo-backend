from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import cache
import json

import pafy
import youtube_dl


with open("nemo/data/streams.json") as json_file:
    streams = json.load(json_file)

original_time = datetime.now()
CACHE_TTL = 18000  # Cache TTL in sec


@cache
def pafy_worker(video_id: str, category: str):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    video = pafy.new(video_url)
    best = video.getbestaudio()
    playurl = best.url
    temp_dict = {
        "category": category,
        "title": video._title,
        "author": video._author,
        "id": video.videoid,
        "duration": video.duration,
        "url": playurl,
        "expiry": video.expiry,
    }
    return temp_dict


def check_cache_expiry():
    current_time = datetime.now()
    diff = current_time - original_time
    return diff.total_seconds() >= CACHE_TTL


def get_all_streams(category):
    if category not in streams.keys():
        return {
            "message": "Invalid category: {}. Should be one of {}".format(
                category, list(streams.keys())
            )
        }

    if check_cache_expiry():
        global original_time
        clear_streams_cache()
        original_time = datetime.now()

    video_urls = streams[category]
    with ThreadPoolExecutor(max_workers=len(video_urls)) as executor:
        args = ((url, category) for url in video_urls)
        result = list(executor.map(lambda p: pafy_worker(*p), args))
    return result


def clear_streams_cache():
    pafy_worker.cache_clear()
    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.cache.remove()


clear_streams_cache()
