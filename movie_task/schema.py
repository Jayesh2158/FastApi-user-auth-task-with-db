from typing import List
from pydantic import BaseModel

# class Comments(BaseModel):
#     id : int
#     user_id : int
#     content : str


# class Movies(BaseModel):
#     id : int 
#     name : str
#     release_year : int
#     genres : str
#     user_id : int
#     comments : List[Comments] = []


class MoviesBase(BaseModel):
    name: str
    release_year: int
    genres: str


class MoviesCreate(MoviesBase):
    pass


class Movies(MoviesBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class User_login(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    movies: List[Movies] = []

    class Config:
        orm_mode = True