# https://docs.deta.sh/docs/base/about
# Using nosql Deta Base

import os

from deta import Deta


def getdetabase(db_name):
    deta = Deta()
    return deta.Base(db_name)


PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
PROJECT_ID = os.getenv("DETA_PROJECT_ID")
DETA_BASE_NEMO = "nemo"
DETA_BASE_TASK = "nemo_tasks"
DETA_BASE_ANALYTICS = "nemo_analytics"
