# https://docs.deta.sh/docs/base/about
# Using nosql Deta Base

import os

from deta import Deta

PROJECT_ID = os.getenv("DETA_PROJECT_ID")
PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
DETA_BASE_NEMO = "nemo"
DETA_BASE_TASK = "nemo_tasks"
DETA_BASE_ANALYTICS = "nemo_analytics"


def getdetabase(db_name):
    deta = Deta(project_key=PROJECT_KEY)
    return deta.Base(db_name)
