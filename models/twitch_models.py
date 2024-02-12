from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Game(BaseModel):
    """Model for Twitch Game"""
    game_id: str
    name: str
    viewers: int = Field(ge=0, default=0)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class UpdateGame(BaseModel):
    name: Optional[str]
    viewers: Optional[int]


class Streamer(BaseModel):
    """Model for Twitch Streamer"""
    streamer_id: str
    is_live: bool
    stream_title: str
    game_id: str
    game_name: str
    user_name: str
    tags: List[str]
    followers: int
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class UpdateStreamer(BaseModel):
    is_live: Optional[bool]
    followers: Optional[int]
    game_id: Optional[str]
    game_name: Optional[str]
    stream_title: Optional[str]
    tags: Optional[List[str]]


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


class UpdateStream(BaseModel):
    title: Optional[str]
    user_id: Optional[str]
    user_name: Optional[str]
    viewers: Optional[int]
    language: Optional[str]
    tags: Optional[List[str]]
