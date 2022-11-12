import requests
import time
import json

from deta import app

"""
Command to set the cron -> `deta cron set "2 hours""`

The purpose of this cron is to periodically hit Nemo Streams API, so that the cache is always updated and 
make the subsequest requests faster. 
"""

NEMO_URL = "https://nemo.deta.dev/nemo"

with open("streams.json") as json_file:
    STREAMS = json.load(json_file)


def get_all_streams_tuple():
    """Generator containing tuple of all the streams."""
    all_stream = ((k, video_id) for k in STREAMS.keys() for video_id in STREAMS[k])
    return all_stream


def fire_and_forget(video_info):
    category, video_id = video_info
    try:
        requests.get(
            NEMO_URL + f"/get-stream-by-id/{category}/{video_id}", timeout=0.0000000001
        )
    except requests.exceptions.ReadTimeout:
        print("completed:", video_id)
        pass


def clear_streams_cache():
    # clear existing cache
    r = requests.get(NEMO_URL + "/clear-stream-cache")
    print(r.json())


@app.lib.cron()
def app(event):
    clear_streams_cache()
    start = time.perf_counter()
    for video_info in get_all_streams_tuple():
        fire_and_forget(video_info)
    end = time.perf_counter()
    print("Total time taken", end - start)
