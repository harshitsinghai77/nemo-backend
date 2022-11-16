import time
import requests
from typing import Dict, List

import youtube_dl

from app.api.crud.nemodeta import NemoAudioStream

VIDEO_LIFESPAN = 60 * 60 * 5  # 5 hours


class YoutubeDLWrapper:

    ydl_opts = {"quiet": True, "prefer_insecure": False, "no_warnings": True}

    def __get_duration(self, duration: int):
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

    def __check_if_stream_valid(self, stream_url) -> bool:
        """Make a head request and check if stream returns 200 status code."""
        if stream_url:
            req = requests.head(stream_url)
            return req.status_code == 200

    def _process_stream(self, video_info: str) -> Dict:
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
                "stream_id": video_id,
                "duration": self.__get_duration(stream_info.get("duration")),
                "url": best_audio["url"],
                "expiry": time.time() + VIDEO_LIFESPAN,
            }

    def get_streams_count_in_detabase(self):
        """Current count of all the streams"""
        return NemoAudioStream.get_streams_count_in_detabase()

    def process_stream(self, video_info: str) -> Dict:
        """Fetch metadata, put it in Deta cache and return the result"""
        _, stream_id = video_info

        # if stream_id exists in cache, fetch and return the stream
        stream = NemoAudioStream.get_audio_stream(stream_id)
        if not stream:
            # If stream_id not in cache, fetch stream metadata
            stream = self._process_stream(video_info)

            # Check if stream metadata url is valid and returning 200 status code
            valid_stream = self.__check_if_stream_valid(stream.get("url"))

            # if stream is valid, put it in the cache
            if valid_stream:
                NemoAudioStream.create_new_audio_stream(stream)
        return stream
