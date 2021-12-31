from typing import List
from pydantic import BaseModel


class CommentsBase(BaseModel):
    content: str


class CommentsCreate(CommentsBase):
    pass


class Comments(CommentsBase):
    id: int
    movie_id: int

    class Config:
        orm_mode = True


class MoviesBase(BaseModel):
    name: str
    release_year: int
    genres: str


class MoviesCreate(MoviesBase):
    pass


class Movies(MoviesBase):
    id: int
    owner_id: int
    comments: List[Comments] = []

    class Config:
        orm_mode = True
