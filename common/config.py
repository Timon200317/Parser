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
    url: str
    name: str

    class Config:
        env_file = ".env"
        env_prefix = "MONGO_DB_"


fast_api_settings = FastAPISettings()
mongo_settings = MongoSettings()
