import logging
import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "config.env"

load_dotenv(ENV_PATH)

DB_NAME = os.environ.get('DB_NAME', "spimex_db")
DB_HOST = os.environ.get('DB_HOST', "postgres")
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_USER = os.environ.get('DB_USER', "spimex_user")
DB_PASS = os.environ.get('DB_PASS', "spimex_password")

RMQ_HOST = os.environ.get('RMQ_HOST', 'localhost')
RMQ_PORT = int(os.environ.get('RMQ_PORT', 5672))
RMQ_USER = os.environ.get('RMQ_USER', 'guest')
RMQ_PASSWORD = os.environ.get('RMQ_PASSWORD', 'guest')
MQ_ROUTING_KEY = os.environ.get('MQ_ROUTING_KEY', 'trading_service')


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
    )