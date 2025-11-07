from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    MONGODB_URI: str = "mongodb_url"
    DB_NAME: str = "gamebot"
    ADMIN_IDS: list[int] = []
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
