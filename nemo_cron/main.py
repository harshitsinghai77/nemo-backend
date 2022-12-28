import time
import requests

from deta import app

"""
Command to set the cron -> `deta cron set "2 hours""`

The purpose of this cron is to periodically hit Nemo Streams API, so that the cache is always updated and 
make the subsequest requests faster. 
"""

NEMO_URL = "https://nemo.deta.dev/nemo"


def clear_streams_cache():
    # clear existing cache
    r = requests.get(NEMO_URL + "/clear-stream-cache")
    print(r.json())


def populate_cache():
    # populate cache
    r = requests.get(NEMO_URL + "/populate-lofi-stream-cache")
    print(r.json())


@app.lib.cron()
def cron_job(event):
    start = time.perf_counter()
    # clear_streams_cache()
    populate_cache()
    end = time.perf_counter()
    print("Total time taken", end - start)
