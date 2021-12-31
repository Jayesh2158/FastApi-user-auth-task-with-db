from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


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
    comment = relationship(
        "Comments", back_populates="movie")
