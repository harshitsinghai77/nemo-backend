# https://deta.space/docs/en/build/fundamentals/data-storage
# Using nosql Deta Base

from deta import Deta

# PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
DETA_BASE_NEMO = "nemo"
DETA_BASE_TASK = "nemo_tasks"
DETA_BASE_ANALYTICS = "nemo_analytics"
DETA_BASE_AUDIO_STREAM = "nemo_audio_stream"
DETA_DRIVE_NEMO_SOUNDS = "nemo-sounds"


def getdetabase(db_name):
    deta = Deta()
    return deta.Base(db_name)


def getdetadrive(drive_name):
    deta = Deta()
    return deta.Drive(drive_name)
