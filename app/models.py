from .database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,
                        server_default=text('now()')
                        )


class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    date_read = Column(String, nullable=False)
    reviewed_by = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,
                        server_default=text('now()'))
    book_reviewed = Column(ForeignKey("books.id"), nullable=False)


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)


class Bookshelves(Base):
    __tablename__ = 'bookshelves'
    id = Column(Integer, primary_key=True, nullable=False)
    book_id = Column(ForeignKey('books.id'), nullable=False)
    user_shelved = Column(String, nullable=False)
    bookshelf = Column(String, nullable=False)


class Likes(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, nullable=False)
    review_id = Column(ForeignKey('reviews.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
