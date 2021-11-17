from pdb import set_trace
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from . import crud, schema, user, services
from fastapi.security import OAuth2PasswordBearer
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

services.create_database()

# .Base.metadata.create_all(bind=engine)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

movies = []


@app.get("/")
def read_root():
    return {"title": "Welcome to Movie mania"}


@app.get("/movies")
def get_movies():
    return movies


@app.get("/movie/id/{movie_id}")
def get_a_movie(movie_id: int):
    movie = movie_id - 1
    return movies[movie]


@app.post("/movies")
def add_movie(movie: schema.Movies):
    # import pdb;pdb.set_trace()
    movies.append(movie.dict())
    return movies[-1]


@app.get("/movie_by_genre/{genres}")
def get_movie_by_geners(genres: str):
    return crud.get_movie_genre(genres)


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movies.pop(movie_id-1)
    return {"task": "deletion successfull"}


@app.post("/users/", response_model=schema.User)
def create_user(user: schema.UserCreate, db: Session = Depends(services.get_db)):
    # import pdb;pdb.set_trace
    db_user = services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="this email already in use."
        )
    return services.create_user(db=db, user=user)


@app.get("/user/", response_model=List[schema.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(services.get_db)):
    users = services.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}/", response_model=schema.User)
def read_user(user_id: int, db: Session = Depends(services.get_db)):
    db_user = services.get_user(db=db, user_id=user_id)

    if db_user is None:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )
    return db_user

@app.post("/users/{user_id}/movies/", response_model=schema.Movies)
def crate_movie(user_id: int, movie: schema.MoviesCreate, db: Session = Depends(services.get_db)):
    db_user = services.get_user(db=db, user_id=user_id)

    if db_user is None:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )

    return services.create_movie(db=db, movie=movie, user_id=user_id)