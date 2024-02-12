import logging
from typing import List

from fastapi import APIRouter, HTTPException, Body, Response, status

from models.twitch_models import Game, Stream, Streamer, UpdateGame, UpdateStreamer, UpdateStream
from parsers.twitch_parser import fetch_games, fetch_streams, fetch_streamers
from services.kafka import KafkaService
from services.twitch_db import TwitchServiceDatabase
from fastapi_cache.decorator import cache

logger = logging.getLogger(__name__)
twitch_mongo = TwitchServiceDatabase()

games_router = APIRouter()
streams_router = APIRouter()
streamers_router = APIRouter()


"""PARSE DATA"""


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


@streamers_router.get("/parse_streamers", response_description="Parse all twitch streamers with kafka")
async def parse_twitch_streamers():
    kafka = KafkaService()
    await kafka.send_message("twitch", b"parse top twitch streams", b"streamers")
    return {"message": "Kafka message sent"}

"""CRUD OPERATIONS"""


@games_router.get(
    "/twitch_games",
    response_description="List of all the twitch games in mongo",
    response_model=List[Game],
)
@cache(expire=15)
def list_twitch_games():
    games = twitch_mongo.list_twitch_games()
    return games


@games_router.put(
    "/{id}",
    response_description="Update a game",
    response_model=Game,
)
def update_twitch_game(id: str, game: UpdateGame = Body(...)):
    existing_game = twitch_mongo.update_twitch_game({"game_id": id}, game)

    if existing_game is not None:
        return existing_game

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"There is no game with an id {id}",
    )


@games_router.delete("/{id}", response_description="Delete a game")
def delete_twitch_game(id: str, response: Response):
    delete_result = twitch_mongo.delete_twitch_game({"game_id": id})

    if delete_result == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no game with an id {id}",
        )


"""Streams CRUD"""


@streams_router.get(
    "/twitch_streams",
    response_description="List of all the twitch streams in mongo",
    response_model=List[Stream],
)
@cache(expire=15)
def list_twitch_streams():
    streams = twitch_mongo.list_twitch_streams()
    return streams


@streams_router.get(
    "/{id}",
    response_description="Retrieve a specific stream by id",
    response_model=Stream,
)
@cache(expire=15)
def get_twitch_stream(id: str):
    stream = twitch_mongo.find_twitch_stream({"stream_id": id})
    if stream is not None:
        return stream
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no stream with an id {id}",
        )


@streams_router.put(
    "/{id}",
    response_description="Update a stream",
    response_model=Stream,
)
def update_twitch_stream(id: str, stream: UpdateStream = Body(...)):
    existing_stream = twitch_mongo.update_twitch_stream({"stream_id": id}, stream)

    if existing_stream is not None:
        return existing_stream
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no stream with an id {id}",
        )


@streams_router.delete("/{id}", response_description="Delete a stream")
def delete_twitch_stream(id: str, response: Response):
    delete_result = twitch_mongo.delete_twitch_stream({"stream_id": id})

    if delete_result == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no stream with an id {id}",
        )


"""Streamers CRUD"""


@streamers_router.get(
    "/twitch_streamers",
    response_description="List of all the twitch streamers in mongo",
    response_model=List[Streamer],
)
@cache(expire=15)
def list_twitch_streamers():
    streamers = twitch_mongo.list_twitch_streamers()
    return streamers


@streamers_router.get(
    "/{id}",
    response_description="Retrieve a specific streamer by id",
    response_model=Streamer,
)
@cache(expire=15)
def get_twitch_streamer(id: str):
    streamer = twitch_mongo.find_twitch_streamer({"streamer_id": id})
    if streamer is not None:
        return streamer
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no streamer with an id {id}",
        )


@streamers_router.put(
    "/{id}",
    response_description="Update a streamer",
    response_model=Streamer,
)
def update_twitch_streamer(id: str, streamer: UpdateStreamer = Body(...)):
    existing_streamer = twitch_mongo.update_twitch_streamer(
        {"streamer_id": id}, streamer
    )

    if existing_streamer is not None:
        return existing_streamer
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no streamer with an id {id}",
        )


@streamers_router.delete("/{id}", response_description="Delete a streamer")
def delete_twitch_streamer(id: str, response: Response):
    delete_result = twitch_mongo.delete_twitch_streamer({"streamer_id": id})

    if delete_result == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no streamer with an id {id}",
        )


"""Games CRUD"""


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


@streamers_router.get(
    "/twitch_streamers_test",
    response_description="List of all the twitch streames in mongo",
)
async def parse_streamers_test():
    streamers = await fetch_streamers()
    return streamers
