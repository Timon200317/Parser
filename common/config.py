from pydantic_settings import BaseSettings, SettingsConfigDict


class FastAPISettings(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", env_prefix="FASTAPI_")


class MongoSettings(BaseSettings):
    url: str
    name: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MONGO_")


fast_api_settings = FastAPISettings()
mongo_settings = MongoSettings()
