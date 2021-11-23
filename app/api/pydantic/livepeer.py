from pydantic import BaseModel


class LivepeerStream(BaseModel):
    stream_name: str


class LivepeerStreamStatus(BaseModel):
    stream_id: str
