import logging
from typing import List

from fastapi import APIRouter

from models.twitch_models import Game, Stream
from parsers.twitch_parser import fetch_games, fetch_streams
from services.kafka import KafkaService
from services.twitch_db import TwitchServiceDatabase
from fastapi_cache.decorator import cache

logger = logging.getLogger(__name__)
twitch_mongo = TwitchServiceDatabase()

games_router = APIRouter()
streams_router = APIRouter()


@games_router.get("/parse_games", response_description="Parse all twitch games with kafka")
async def parse_twitch_games():
    kafka = KafkaService()
    await kafka.send_message("twitch", b"parse top twitch games", b"games")
    return {"message": "Kafka message sent"}


@streams_router.get("/parse_streams", response_description="Parse all twitch streams with kafka")
async def parse_twitch_streams():
    kafka = KafkaService()
    await kafka.send_message("twitch", b"parse top twitch streams", b"streams")
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


@streams_router.get(
    "/twitch_streams",
    response_description="List of all the twitch streams in mongo",
    response_model=List[Stream],
)
@cache(expire=360)
def list_twitch_streams():
    streams = twitch_mongo.list_twitch_streams()
    return streams


@games_router.get(
    "/twitch_games_test",
    response_description="List of all the twitch games in mongo",
)
async def parse_games_test():
    games = await fetch_games()
    return games


@streams_router.get(
    "/twitch_streams_test",
    response_description="List of all the twitch streams in mongo",
)
async def parse_streams_test():
    streams = await fetch_streams()
    return streams
