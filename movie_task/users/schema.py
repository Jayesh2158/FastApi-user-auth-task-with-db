from typing import List, Optional
from pydantic import BaseModel, EmailStr
from ..movies_stuff import schema as movie_schema


class User_login(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    movies: List[movie_schema.Movies] = []

    class Config:
        orm_mode = True


class ShowUser(BaseModel):
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Reset_password(BaseModel):
    reset_token: str
    password: str
    confirm_password: str
