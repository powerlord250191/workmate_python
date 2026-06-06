from dotenv import load_dotenv
from config import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASS
from models import *

load_dotenv()
DATABASE_URL = (f"postgresql+asyncpg://"
                f"{DB_USER}:{DB_PASS}@"
                f"{DB_HOST}:{DB_PORT}/"
                f"{DB_NAME}")

SYNC_DATABASE_URL = (f"postgresql://"
                     f"{DB_USER}:{DB_PASS}@"
                     f"{DB_HOST}:{DB_PORT}/"
                     f"{DB_NAME}")


def initial_db(engine):
    Base.metadata.create_all(engine)
