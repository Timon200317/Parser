import logging
from typing import List

from pydantic import TypeAdapter
from pymongo import MongoClient

from common.mongo_config import MONGO_URI, MONGO_INITDB_DATABASE
from models.twitch_models import Game, Stream, Streamer

logger = logging.getLogger()


class TwitchServiceDatabase:
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.database = self.mongo_client[MONGO_INITDB_DATABASE]

        try:
            self.mongo_client.admin.command("ping")
            logger.info(
                "Pinged your deployment. You successfully connected to MongoDB!"
            )
        except Exception as e:
            logger.info(
                "Mongo in not connected"
            )

    """CRUD Functions for work with MongoDB"""

    async def parse_twitch_games(self, games: List[Game]):
        for game in games:
            if (
                    # if model have this instance count_document will be equal 1
                    self.database["Game"].count_documents(
                        {"game_id": game.game_id}
                    )
                    > 0
            ):
                # update exist data
                self.database["Game"].find_one_and_replace(
                    {"game_id": game.game_id}, game.model_dump()
                )
            else:
                # write data in model
                self.database["Game"].insert_one(game.model_dump())

    async def parse_twitch_streams(self, streams: List[Stream]):
        for stream in streams:
            if (
                    # if model have this instance count_document will be equal 1
                    self.database["Stream"].count_documents(
                        {"user_id": stream.user_id}
                    )
                    > 0
            ):
                # update exist data
                self.database["Stream"].find_one_and_replace(
                    {"user_id": stream.user_id}, stream.model_dump()
                )
            else:
                # write data in model
                self.database["Stream"].insert_one(stream.model_dump())

    async def parse_twitch_streamers(self, streamers: List[Streamer]):
        for streamer in streamers:
            if (
                    # if model have this instance count_document will be equal 1
                    self.database["Streamer"].count_documents(
                        {"streamer_id": streamer.streamer_id}
                    )
                    > 0
            ):
                # update exist data
                self.database["Streamer"].find_one_and_replace(
                    {"streamer_id": streamer.streamer_id}, streamer.model_dump()
                )
            else:
                # write data in model
                self.database["Streamer"].insert_one(streamer.model_dump())

    def list_twitch_games(self):
        games_dict = self.database["Game"].find()
        type_adapter = TypeAdapter(List[Game])
        games = type_adapter.validate_python(games_dict)
        return games

    def list_twitch_streams(self):
        streams_dict = self.database["Stream"].find()
        type_adapter = TypeAdapter(List[Stream])
        streams = type_adapter.validate_python(streams_dict)
        return streams

    def list_twitch_streamers(self):
        streamers_dict = self.database["Streamer"].find()
        type_adapter = TypeAdapter(List[Streamer])
        streamers = type_adapter.validate_python(streamers_dict)
        return streamers

