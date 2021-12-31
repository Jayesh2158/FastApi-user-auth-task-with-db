import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.sqltypes import DateTime
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = deferred(Column(String))
    user_profile_image = Column(String, nullable=True)
    movies = relationship("Movies", backref='movie')


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
