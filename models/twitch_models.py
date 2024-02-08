from datetime import datetime
from pydantic import BaseModel, Field


class Game(BaseModel):
    """Model for Twitch Game"""
    game_id: str
    name: str
    viewers: int = Field(ge=0, default=0)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class Streamer(BaseModel):
    """Model for Twitch Streamer"""
    username: str = Field(max_length=128)
    platform: str = Field(max_length=50)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class TwitchStream(BaseModel):
    """Model for Twitch Stream"""
    title: str = Field(max_length=100)
    viewers: int
    streamer: Streamer
    game: Game
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)
