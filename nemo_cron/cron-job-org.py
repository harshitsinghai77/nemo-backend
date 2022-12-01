import requests
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

Authorization = f"Bearer {os.getenv('CRON_JOB_ORG_AUTHORIZATION')}"

NEMO_URL = "https://nemo.deta.dev/nemo"
cookies = {
    "refreshToken": "Qs8lanPkPasB1rdl5RtPMJHmHVBxjYnTvHGYJdQDKi3ui5H9iZspBNRtGKb80v9r",
}

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": Authorization,
    "Connection": "keep-alive",
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
    # 'Cookie': 'refreshToken=Qs8lanPkPasB1rdl5RtPMJHmHVBxjYnTvHGYJdQDKi3ui5H9iZspBNRtGKb80v9r',
    "Origin": "https://console.cron-job.org",
    "Referer": "https://console.cron-job.org/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-GPC": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36",
    "X-API-Method": "CreateJob",
    "X-UI-Language": "en",
}


def make_request(title, url):

    json_data = {
        "job": {
            "title": title,
            "url": url,
            "enabled": True,
            "saveResponses": False,
            "requestTimeout": 30,
            "redirectSuccess": False,
            "auth": {
                "enable": False,
                "user": "",
                "password": "",
            },
            "notification": {
                "onSuccess": True,
                "onDisable": True,
                "onFailure": False,
            },
            "requestMethod": 0,
            "extendedData": {
                "body": "",
                "headers": {},
            },
            "schedule": {
                "mdays": [
                    -1,
                ],
                "wdays": [
                    -1,
                ],
                "months": [
                    -1,
                ],
                "hours": [
                    -1,
                ],
                "minutes": [
                    0,
                ],
                "timezone": "UTC",
            },
        },
    }

    response = requests.post(
        "https://api.cron-job.org/", cookies=cookies, headers=headers, json=json_data
    )

    if response and response.status_code == 200:
        print("sucess", url)
    else:
        while True:
            print("retrying", url)
            time.sleep(4)
            response = requests.post(
                "https://api.cron-job.org/",
                cookies=cookies,
                headers=headers,
                json=json_data,
            )
            if response and response.status_code == 200:
                print("retrying success", url)
                break
    print()


def delete():
    json_data = {
        "jobIds": [],
        "action": "delete",
    }

    response = requests.post(
        "https://api.cron-job.org/", cookies=cookies, headers=headers, json=json_data
    )
    print("response", response.json())


def get_all_streams_tuple():
    with open("app/api/data/streams.json") as json_file:
        STREAMS = json.load(json_file)

        all_stream = ((k, video_id) for k in STREAMS.keys() for video_id in STREAMS[k])
    return all_stream


def main():
    for category, video_id in get_all_streams_tuple():
        title = f"{category}/{video_id}"
        url = NEMO_URL + f"/get-stream-by-id/{category}/{video_id}"
        make_request(title, url)
        # time.sleep(5)


main()
