import datetime
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.sqltypes import DateTime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = deferred(Column(String))
    movies = relationship("Movies", back_populates="owner")


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie = relationship("Movies", back_populates="comment")


class Movies(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    release_year = Column(Integer, index=True)
    genres = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="movies")
    comment = relationship(
        "Comments", back_populates="movie")


class Forgotpass_code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    reset_code = Column(String, index=True)
    status = Column(String(1), index=True)
    expired_in = Column(DateTime, default=datetime.datetime.utcnow)


class Black_list(Base):
    __tablename__ = "black-list"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True)