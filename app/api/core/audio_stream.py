import time
from typing import Dict, List

import youtube_dl

from app.api.crud.nemodeta import NemoAudioStream

VIDEO_LIFESPAN = 60 * 60 * 5  # 5 hours


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

    def __process_stream(self, video_info: str) -> Dict:
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
                "duration": self.get_duration(stream_info.get("duration")),
                "url": best_audio["url"],
                "expiry": time.time() + VIDEO_LIFESPAN,
            }

    def process_stream(self, video_info: str) -> Dict:
        """Put results in Deta cache and return the results"""
        _, stream_id = video_info

        # if stream_id exists in cache, fetch and return the stream
        stream = NemoAudioStream.get_audio_stream(stream_id)
        if not stream:
            # If key not in cache, calculate the stream and put it in cache.
            stream = self.__process_stream(video_info)
            NemoAudioStream.create_new_audio_stream(stream)

        return stream
