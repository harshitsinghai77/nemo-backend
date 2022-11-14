import time
import requests

from deta import app

"""
Command to set the cron -> `deta cron set "2 hours""`

The purpose of this cron is to periodically hit Nemo Streams API, so that the cache is always updated and 
make the subsequest requests faster. 
"""

NEMO_URL = "https://nemo.deta.dev/nemo"

# with open("./streams.json") as json_file:
#     STREAMS = json.load(json_file)
#     print("STREAMS: ", STREAMS)


# def get_all_streams_tuple():
#     """Generator containing tuple of all the streams."""
#     all_stream = ((k, video_id) for k in STREAMS.keys() for video_id in STREAMS[k])
#     return all_stream


# def divide_chunks(l, n):
#     # looping till length l
#     for i in range(0, len(l), n):
#         yield l[i : i + n]


# async def fire_and_forget(video_info, client):
#     category, video_id = video_info
#     url = NEMO_URL + f"/get-stream-by-id/{category}/{video_id}"
#     print("url: ", url)
#     await client.get(url)
#     await client.close()


def clear_streams_cache():
    # clear existing cache
    r = requests.get(NEMO_URL + "/clear-stream-cache")
    print(r.json())


def update_cache():
    # update cache
    r = requests.get(NEMO_URL + "/populate-lofi-stream-cache")
    print(r.json())


@app.lib.cron()
def cron_job(event):
    start = time.perf_counter()
    clear_streams_cache()
    update_cache()
    end = time.perf_counter()
    print("Total time taken", end - start)
