# https://docs.deta.sh/docs/base/about
# Using nosql Deta Base

import os

from deta import Deta

PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
PROJECT_ID = os.getenv("DETA_PROJECT_ID")
DETA_TASK_BASENAME = "nemo_tasks"

deta = Deta(PROJECT_KEY)
deta_db = deta.Base("nemo")
deta_analytics_db = deta.Base("nemo_analytics")
deta_task_db = deta.Base(DETA_TASK_BASENAME)
