import os
import sys

sys.path.append(os.path.dirname(".."))

import json
from app.api.core.audio_stream import YoutubeDLWrapper
from app.api.core.nemo_stream import clear_streams_cache, populate_stream_cache

with open("app/api/data/streams.json") as json_file:
    STREAMS = json.load(json_file)

yt = YoutubeDLWrapper()

# def create_stream_cache():
#     all_stream = ((k, video_id) for k in STREAMS.keys() for video_id in STREAMS[k])
#     for stream_info in all_stream:
#         print("stream_info: ", stream_info)
#         res = yt._YoutubeDDL__process_stream(stream_info)
#         print("res: ", res)
#         print()

print(yt.get_streams_count_in_detabase())
