from pydantic import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    # Server settings
    HOST: str
    PORT: int

    # Service settings
    RESERVATION_PUSH: bool = True
    TRANSFER_RECORDINGS: bool = True

    SESSION_START_TIME_HOUR: str = "15"
    SESSION_START_TIME_MINUTE: str = "40"

    SESSION_END_TIME_HOUR: str = "22"
    SESSION_END_TIME_MINUTE: str = "45"

    # Agora settings
    AGORA_CUSTOMER_KEY: str
    AGORA_CUSTOMER_SECRET: str

    # Agora App ID & Cert
    AGORA_APP_ID: str
    AGORA_APP_CERT: str

    # firebase-admin-SDK json file path
    GOOGLE_APPLICATION_CREDENTIALS: str

    # firebase cloud messaging Token
    FCM_TOKEN: str

    # Google Cloud Storage Key
    GCLOUD_ACCESS_KEY: str
    GCLOUD_SECRET: str

    # FTP settings
    FTP_HOST: str
    FTP_PORT: int
    FTP_USERNAME: str
    FTP_PASSWORD: str
    FTP_PROFILE_PATH: str
    FTP_RECORDING_PATH: str
    FTP_SNS_PATH: str

    # default user image address
    DEFAULT_IMG: str

    # Mongo DB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


load_dotenv()
settings = Settings()
