from pydantic import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    # Server settings
    HOST: str
    PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


load_dotenv()
settings = Settings()
