import datetime
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, deferred, relationship
from sqlalchemy.sql.sqltypes import DateTime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = deferred(Column(String))
    user_profile_image = Column(String, nullable=True)
    movies = relationship("Movies", back_populates="owner")


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie = relationship("Movies", backref=backref(
        "comment", cascade="all, delete-orphan"))


class Movies(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    release_year = Column(Integer, index=True)
    genres = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", cascade="save-update")
    comment = relationship(
        "Comments", cascade="all, delete-orphan")


class Forgotpass_code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    reset_code = Column(String, index=True)
    expired_in = Column(DateTime, default=datetime.datetime.utcnow)


class Black_list(Base):
    __tablename__ = "black-list"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True)
