from database import Base
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Genre(Base):
    __tablename__ = "genre"

    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    genre_name: Mapped[str] = mapped_column(String(50))

    books: Mapped[list["Book"]] = relationship(back_populates="genre")


class Author(Base):
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_author: Mapped[str] = mapped_column(String(100))

    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = 'book'

    book_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[int] = mapped_column(String(150))
    price: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(Integer)

    author_id: Mapped[int] = mapped_column(ForeignKey('author.author_id'))
    genre_id: Mapped[int] = mapped_column(ForeignKey('genre.genre_id'))

    genre: Mapped['Genre'] = relationship(back_populates='books')
    author: Mapped['Author'] = relationship(back_populates='books')
    buy_books: Mapped[list['BuyBook']] = relationship(back_populates='book')


class City(Base):
    __tablename__ = 'city'

    city_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_city: Mapped[str] = mapped_column(String(100))
    days_delivery: Mapped[int] = mapped_column(Integer)
    clients: Mapped[list['Client']] = relationship(back_populates='city')


class Client(Base):
    __tablename__ = "client"

    client_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_client: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50))
    city_id: Mapped[int] = mapped_column(ForeignKey('city.city_id'))
    city: Mapped['City'] = relationship(back_populates='clients')
    buys: Mapped[list['Buy']] = relationship('client')


class Buy(Base):
    __tablename__ = 'buy'

    buy_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buy_description: Mapped[str] = mapped_column(String(300))
    client_id: Mapped[int] = mapped_column(ForeignKey('client.client_id'))
    client: Mapped['Client'] = relationship(back_populates='buys')
    buy_books: Mapped[list['BuyBook']] = relationship(back_populates='buy')
    buy_step: Mapped[list['BuyStep']] = relationship(back_populates='buy')


class BuyBook(Base):
    __tablename__ = 'buy_book'

    buy_book_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(Integer)

    buy_id: Mapped[int] = mapped_column(ForeignKey('buy.buy_id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('book.book_id'))

    buy: Mapped['Buy'] = relationship(back_populates='buy_books')
    book: Mapped['Book'] = relationship(back_populates='buy_books')


class Step(Base):
    __tablename__ = 'step'

    step_id: Mapped[int] = mapped_column(primary_key=True)
    name_step: Mapped[str] = mapped_column(String)

    buy_steps: Mapped[list['BuyStep']] = relationship(back_populates='step')


class BuyStep(Base):
    __tablename__ = 'buy_step'

    buy_step_id: Mapped[int] = mapped_column(primary_key=True)

    buy_id: Mapped[int] = mapped_column(ForeignKey('buy.buy_id'))
    step_id: Mapped[int] = mapped_column(ForeignKey('step.step_id'))

    date_step_beg: Mapped[DateTime] = mapped_column(DateTime)
    date_step_end: Mapped[DateTime] = mapped_column(DateTime)

    buy: Mapped['Buy'] = relationship(back_populates='buy_steps')
    step: Mapped['Step'] = relationship(back_populates='buy_steps')
