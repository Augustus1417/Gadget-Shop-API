from pydantic_settings import BaseSettings
from pathlib import Path

# get the .env file path from outside the app dir
# this seems to not work well on windows machines
env_path = Path(__file__).resolve().parent.parent / '.env' 

class Settings(BaseSettings):
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    DATABASE: str
    PASS_HASH: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CORS_ORIGINS: str

    class Config:
        env_file = str(env_path)

settings = Settings()