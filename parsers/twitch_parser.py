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


async def fetch_streamers():
    headers = await get_auth_for_api()
    streams = await fetch_streams()
    streamers = []

    for stream in streams:
        users_url = "https://api.twitch.tv/helix/users"
        users_params = {"first": 100, "id": str(stream.user_id)}
        async with aiohttp.ClientSession() as client:
            response = await client.get(users_url, headers=headers, params=users_params)
            users_data_json = await response.json()
            users_data = users_data_json["data"]
            for user in users_data:
                channel_url = "https://api.twitch.tv/helix/channels"
                followers_url = "https://api.twitch.tv/helix/channels/followers"
                channel_params = {"broadcaster_id": int(user["id"])}
                channel_response = await client.get(
                    channel_url, headers=headers, params=channel_params
                )
                followers_response = await client.get(
                    followers_url, headers=headers, params=channel_params
                )
                followers_json = await followers_response.json()
                followers = followers_json["total"]
                channel_data_json = await channel_response.json()
                channel_data = channel_data_json["data"][0]
                streamers.append(
                    Streamer(
                        streamer_id=channel_data["broadcaster_id"],
                        user_name=channel_data["broadcaster_name"],
                        is_live=True,
                        followers=followers,
                        game_id=channel_data["game_id"],
                        game_name=channel_data["game_name"],
                        stream_title=channel_data["title"],
                        tags=channel_data["tags"],
                        date_item_created=user["created_at"],
                    )
                )

    return streamers


async def insert_twitch_games_in_mongo():
    games = await fetch_games()
    await twitch_mongo.parse_twitch_games(games)


async def insert_twitch_streams_in_mongo():
    streams = await fetch_streams()
    await twitch_mongo.parse_twitch_streams(streams)


async def insert_twitch_streamers_in_mongo():
    streams = await fetch_streamers()
    await twitch_mongo.parse_twitch_streamers(streams)
