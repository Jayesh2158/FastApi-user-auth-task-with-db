from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # movies = relationship("Movies", back_populates="user")
    movies = relationship("Movies", back_populates="owner")


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)


class Movies(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    release_year = Column(Integer, index=True)
    genres = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    owner = relationship("User", back_populates="movies")






