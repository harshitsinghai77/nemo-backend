from pydantic import BaseModel


class LivepeerStream(BaseModel):
    stream_name: str
