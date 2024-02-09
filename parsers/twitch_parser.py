import aiohttp

from common.twitch_config import twitch_settings
from models.twitch_models import Game, Stream, Streamer
from services.twitch_db import TwitchServiceDatabase

twitch_mongo = TwitchServiceDatabase()


async def get_auth_for_api():
    token_url = "https://id.twitch.tv/oauth2/token"
    token_params = {
        "client_id": twitch_settings.client_id,
        "client_secret": twitch_settings.client_secret,
        "grant_type": "client_credentials",
    }

    async with aiohttp.ClientSession() as client:
        response_token = await client.post(token_url, data=token_params)
        # get json from response
        data_token = await response_token.json()
    headers = {
        "Client-ID": twitch_settings.client_id,
        "Authorization": "Bearer " + data_token["access_token"],
    }

    return headers


async def fetch_games():
    headers = await get_auth_for_api()
    games_url = "https://api.twitch.tv/helix/games/top"
    games = []

    games_params = {"first": 100}
    async with aiohttp.ClientSession() as client:
        response = await client.get(games_url, headers=headers, params=games_params)
        json_data = await response.json()
        data = json_data["data"]
        streams_url = "https://api.twitch.tv/helix/streams"

        for game in data:
            streams_params = {"first": 100, "game_id": game["id"]}
            streams_response = await client.get(
                streams_url, headers=headers, params=streams_params
            )
            streams_data_json = await streams_response.json()
            streams_data = streams_data_json["data"]
            viewers = sum(streams["viewer_count"] for streams in streams_data)
            games.append(
                Game(game_id=game["id"], name=game["name"], viewers=viewers)
            )

    return games


async def fetch_streams():
    headers = await get_auth_for_api()
    streams_url = "https://api.twitch.tv/helix/streams"
    streams = []

    streams_params = {"first": 100}
    async with aiohttp.ClientSession() as client:
        response = await client.get(streams_url, headers=headers, params=streams_params)
        json_data = await response.json()
        data = json_data["data"]

        for stream in data:

            stream_model = Stream(
                stream_id=stream["id"],
                # game_name=stream["game_name"],
                # game_id=stream["game_id"],
                type=stream["type"],
                title=stream["title"],
                viewers=stream["viewer_count"],
                language=stream["language"],
                tags=stream["tags"],
                user_id=stream["user_id"],
                user_name=stream["user_name"],
            )
            streams.append(stream_model)

    return streams


async def insert_twitch_games_in_mongo():
    games = await fetch_games()
    await twitch_mongo.parse_twitch_games(games)


async def insert_twitch_streams_in_mongo():
    streams = await fetch_streams()
    await twitch_mongo.parse_twitch_streams(streams)
