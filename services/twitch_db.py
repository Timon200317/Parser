import logging
from typing import List

from pydantic import TypeAdapter
from pymongo import MongoClient

from common.mongo_config import MONGO_URI, MONGO_INITDB_DATABASE
from models.twitch_models import Game, Stream, Streamer, UpdateStreamer, UpdateStream, UpdateGame

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

    def find_twitch_game(self, query):
        game_dict = self.database["TwitchGameModels"].find_one(query)
        if game_dict is None:
            return None
        type_adapter = TypeAdapter(Game)
        game = type_adapter.validate_python(game_dict)
        return game

    def update_twitch_game(self, query, update: UpdateGame):
        update = {
            key: value
            for key, value in update.model_dump().items()
            if value is not None
        }
        update_result = self.database["Game"].update_one(
            query, {"$set": update}
        )
        if update_result.modified_count == 0:
            return None
        existing_game_dict = self.database["Game"].find_one(update)
        type_adapter = TypeAdapter(Game)
        existing_game = type_adapter.validate_python(existing_game_dict)
        return existing_game

    def delete_twitch_game(self, query):
        delete_result = self.database["Game"].delete_one(query)
        return delete_result.deleted_count

    def list_twitch_streams(self):
        streams_dict = self.database["Stream"].find()
        type_adapter = TypeAdapter(List[Stream])
        streams = type_adapter.validate_python(streams_dict)
        return streams

    def find_twitch_stream(self, query):
        stream_dict = self.database["Stream"].find_one(query)
        if stream_dict is None:
            return None
        type_adapter = TypeAdapter(Stream)
        stream = type_adapter.validate_python(stream_dict)
        return stream

    def update_twitch_stream(self, query, update: UpdateStream):
        # Create the update dictionary with non-None values from UpdateStream
        update_data = {
            key: value
            for key, value in update.model_dump().items()
            if value is not None
        }

        # Print or log the update data for debugging
        print("Update Data:", update_data)

        # Perform the update using update_one
        update_result = self.database["Stream"].update_one(
            query, {"$set": update_data}
        )

        # Check if any documents were modified
        if update_result.modified_count == 0:
            return None

        # Find the updated document and convert it back to Stream instance
        existing_item_dict = self.database["Stream"].find_one(query)
        type_adapter = TypeAdapter(Stream)
        existing_item = type_adapter.validate_python(existing_item_dict)

        return existing_item

    def delete_twitch_stream(self, query):
        delete_result = self.database["Stream"].delete_one(query)
        return delete_result.deleted_count

    def list_twitch_streamers(self):
        streamers_dict = self.database["Streamer"].find()
        type_adapter = TypeAdapter(List[Streamer])
        streamers = type_adapter.validate_python(streamers_dict)
        return streamers

    def find_twitch_streamer(self, query):
        streamer_dict = self.database["Streamer"].find_one(query)
        if streamer_dict is None:
            return None
        type_adapter = TypeAdapter(Streamer)
        streamer = type_adapter.validate_python(streamer_dict)
        return streamer

    def update_twitch_streamer(self, query, update: UpdateStreamer):
        # Create the update dictionary with non-None values from UpdateStreamer
        update_data = {
            key: value
            for key, value in update.model_dump().items()
            if value is not None
        }

        # Print or log the update data for debugging
        print("Update Data:", update_data)

        # Perform the update using update_one
        update_result = self.database["Streamer"].update_one(
            query, {"$set": update_data}
        )

        # Check if any documents were modified
        if update_result.modified_count == 0:
            return None

        # Find the updated document and convert it back to Streamer instance
        existing_item_dict = self.database["Streamer"].find_one(query)
        type_adapter = TypeAdapter(Streamer)
        existing_item = type_adapter.validate_python(existing_item_dict)

        return existing_item

    def delete_twitch_streamer(self, query):
        delete_result = self.database["Streamer"].delete_one(query)
        return delete_result.deleted_count
