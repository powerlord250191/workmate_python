from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from models import Base, Genre, Author, Book, City, Client, Buy, BuyBook, BuyStep


if __name__ == "__main__":

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)

    Base.metadata.create_all(engine)
    print("✅ Таблицы успешно созданы!")
