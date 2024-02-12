import asyncio

import aioredis
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from dotenv import load_dotenv

from common.config import FastAPISettings, get_fastapi_settings, MongoConfig, \
    get_mongo_config, redis_settings
from routes.lamoda_routes import category_router as lamoda_category_router, item_router as lamoda_item_router
from routes.twitch_routes import (games_router as twitch_games_router, streams_router as twitch_streams_router,
                                  streamers_router as twitch_streamers_router)
from services.ExceptionHandler import ExceptionHandlerMiddleware
from services.kafka import KafkaService

load_dotenv()
app = FastAPI()
kafka = KafkaService()

app.add_middleware(ExceptionHandlerMiddleware)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{redis_settings.host}:{redis_settings.port}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


async def consume():
    await kafka.consume_messages(["lamoda", "twitch"])


asyncio.create_task(consume())


@app.get("/")
async def read_root(
        fastapi_settings: FastAPISettings = Depends(get_fastapi_settings),
        database: MongoConfig = Depends(get_mongo_config),
):
    return {"message": "Hello, World!", "fastapi_settings": fastapi_settings.model_dump(),
            "mongo_settings": database.mongo_uri
            }


app.include_router(
    lamoda_category_router,
    tags=["Lamoda categories"],
    prefix="/api/v1/lamoda-category",
)

app.include_router(
    lamoda_item_router,
    tags=["Lamoda items"],
    prefix="/api/v1/lamoda-items",
)

app.include_router(
    twitch_games_router,
    tags=["Twitch games"],
    prefix="/api/v1/twitch-games",
)

app.include_router(
    twitch_streams_router,
    tags=["Twitch streams"],
    prefix="/api/v1/twitch-streams",
)

app.include_router(
    twitch_streamers_router,
    tags=["Twitch streamers"],
    prefix="/api/v1/twitch-streamers",
)


@app.get("/value_error")
def value_error_route():
    raise ValueError("This is a ValueError")


# Пример маршрута, вызывающего FileNotFoundError
@app.get("/file_not_found")
def file_not_found_route():
    raise FileNotFoundError("This is a FileNotFoundError")


# Пример маршрута, вызывающего PermissionError
@app.get("/permission_error")
def permission_error_route():
    raise PermissionError("This is a PermissionError")


# Пример маршрута, вызывающего общее исключение
@app.get("/generic_exception")
def generic_exception_route():
    raise Exception("This is a generic Exception")
