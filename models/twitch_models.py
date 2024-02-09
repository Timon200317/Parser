from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Game(BaseModel):
    """Model for Twitch Game"""
    game_id: str
    name: str
    viewers: int = Field(ge=0, default=0)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class Streamer(BaseModel):
    """Model for Twitch Streamer"""
    user_id: str
    user_name: str
    followers: int
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class Stream(BaseModel):
    """Model for Twitch Stream"""
    stream_id: str
    user_id: str
    user_name: str
    type: str
    title: str
    viewers: int
    language: str
    tags: List[str]
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)
