import logging
from typing import List

from fastapi import APIRouter

from models.twitch_models import Game
from parsers.twitch_parser import fetch_games
from services.kafka import KafkaService
from services.twitch_db import TwitchServiceDatabase
from fastapi_cache.decorator import cache

logger = logging.getLogger(__name__)
twitch_mongo = TwitchServiceDatabase()

games_router = APIRouter()


@games_router.get("/parse_games", response_description="Parse all twitch games")
async def parse_twitch_games():
    kafka = KafkaService()
    await kafka.send_message("twitch", b"parse top twitch games", b"games")
    return {"message": "Kafka message sent"}


@games_router.get(
    "/twitch_games",
    response_description="List of all the twitch games in mongo",
    response_model=List[Game],
)
@cache(expire=360)
def list_twitch_games():
    games = twitch_mongo.list_twitch_games()
    return games


@games_router.get(
    "/twitch_games_test",
    response_description="List of all the twitch games in mongo",
)
async def parse_games_test():
    games = await fetch_games()
    return games
