from fastapi import Depends
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class FastAPISettings(BaseSettings):
    host: str
    port: int

    class Config:
        env_file = ".env"
        env_prefix = "FASTAPI_"


class MongoSettings(BaseSettings):
    root_username: str
    root_password: str
    database: str
    port: int
    host: str

    class Config:
        env_prefix = "MONGO_INITDB_"


class MongoConfig:
    def __init__(self, settings: MongoSettings = Depends(MongoSettings)):
        self.database = settings.database
        self.mongo_uri = f"{settings.database}://{settings.root_username}:{settings.root_password}@{settings.host}:{settings.port}"


# Внедрение зависимости MongoSettings
def get_mongo_settings() -> MongoSettings:
    return MongoSettings()


# Внедрение зависимости MongoDBConfig
def get_mongo_config(settings: MongoSettings = Depends(get_mongo_settings)) -> MongoConfig:
    return MongoConfig(settings=settings)


def get_fastapi_settings() -> FastAPISettings:
    return FastAPISettings()


fast_api_settings = FastAPISettings()
mongo_settings = MongoSettings()
