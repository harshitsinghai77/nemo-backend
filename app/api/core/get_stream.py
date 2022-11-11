import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import cache
from typing import Dict, List

import youtube_dl

with open("app/api/data/streams.json") as json_file:
    streams = json.load(json_file)

last_cache_updated = datetime.now()
VIDEO_LIFESPAN = 60 * 60 * 5  # 5 hours
CACHE_TTL = 16200  # Cache TTL in sec (4.5 hours)


class YoutubeDDL:

    ydl_opts = {"quiet": True, "prefer_insecure": False, "no_warnings": True}

    def get_duration(self, duration: int):
        """Duration of a video (HH:MM:SS). Returns str."""
        if not duration:
            return
        duration = time.strftime("%H:%M:%S", time.gmtime(duration))
        duration = str(duration)
        return duration

    def __get_audio_streams(self, stream_info) -> List:
        "Extract audio streams from the stream_info."
        stream_format = stream_info.get("formats")
        if stream_format:
            return filter(
                lambda x: x.get("acodec") != "none" and x.get("vcodec") == "none",
                stream_format,
            )

    def __sortaudiokey(
        self, x, keybitrate=0, keyftype=0, preftype="any", ftypestrict=True
    ) -> bool:
        """Sort function based on best audio quality."""
        rawbitrate = x.get("abr", 0) * 1024
        extension = x["ext"]
        keybitrate = int(rawbitrate)
        keyftype = preftype == extension
        strict, nonstrict = (keyftype, keybitrate), (keybitrate, keyftype)
        return strict if ftypestrict else nonstrict

    def __getbestaudio(self, audiostreams, preftype="any", ftypestrict=True) -> Dict:
        """Return the highest bitrate audio Stream object."""
        r = max(
            audiostreams,
            key=lambda x: self.__sortaudiokey(
                x, preftype=preftype, ftypestrict=ftypestrict
            ),
        )

        if ftypestrict and preftype != "any" and r.extension != preftype:
            return None
        return r

    def __extract_info(self, video_id: str) -> Dict:
        """Extract stream info based on the given video_id."""
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            try:
                ydl_info = ydl.extract_info(video_id, download=False)
                return ydl_info

            except youtube_dl.utils.DownloadError as e:
                raise IOError(str(e).replace("YouTube said", "Youtube says"))

    @cache
    def process_stream(self, video_info: str) -> Dict:
        """Extract info, process only audio streams and return the best audio.
        video_info:(category, video_id)
        """
        category, video_id = video_info
        if not video_id:
            raise ValueError("Invalid video_id")

        stream_info = self.__extract_info(video_id)
        audio_streams = self.__get_audio_streams(stream_info)
        if audio_streams:
            best_audio = self.__getbestaudio(audio_streams)
            return {
                "category": category,
                "title": stream_info.get("title"),
                "author": stream_info.get("uploader"),
                "id": video_id,
                "duration": self.get_duration(stream_info.get("duration")),
                "url": best_audio["url"],
                "expiry": time.time() + VIDEO_LIFESPAN,
            }


YOUTUBE_DDL = YoutubeDDL()


def check_cache_expiry():
    """Check if cache is expired. By default 4.5 hrs."""
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
    all_ids = [(k, video_id) for k in streams.keys() for video_id in streams[k]]

    max_worker = 10
    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        executor.map(YOUTUBE_DDL.process_stream, all_ids)
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
    video_urls = [(category, url) for url in video_urls]
    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        result = list(executor.map(YOUTUBE_DDL.process_stream, video_urls))

    return result


def get_stream_by_id(category: str, video_id: str):
    """Get Any stream by id."""
    return YOUTUBE_DDL.process_stream((category, video_id))


def clear_streams_cache():
    "Clear function cache and remove Youtube DL cache."
    YOUTUBE_DDL.process_stream.cache_clear()
    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.cache.remove()


update_cache()
