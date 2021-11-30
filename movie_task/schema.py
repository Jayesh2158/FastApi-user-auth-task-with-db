from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


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


class User_login(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    movies: List[Movies] = []

    class Config:
        orm_mode = True


class ShowUser(BaseModel):
    id: int
    email: str
