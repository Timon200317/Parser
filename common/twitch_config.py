from pydantic_settings import BaseSettings


class TwitchSettings(BaseSettings):
    id: str
    client_secret: str

    class Config:
        env_file = ".env"
        env_prefix = "TWITCH_APP_"


twitch_settings = TwitchSettings()
