from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "config.env"

load_dotenv(ENV_PATH)

DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')


class Config:
    DATABASE_URL = (f"postgresql+asyncpg://"
                    f"{DB_USER}:{DB_PASS}@"
                    f"{DB_HOST}:{DB_PORT}/"
                    f"{DB_NAME}")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_RESET_TIME = "14:11"  # Время сброса кэша