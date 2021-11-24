from datetime import timedelta
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from jose.exceptions import JWEError
from . import schema, services, jwt_handlers, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt


services.create_database()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def get_current_user(
        db: Session = Depends(services.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            jwt_handlers.SECRET_KEY,
            algorithms=[jwt_handlers.ALGORITHM],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        token_data = schema.TokenData(username=user_id)
    except JWEError:
        raise credentials_exception
    user = db.query(models.User).filter(
        models.User.id == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/users/", response_model=schema.User)
def create_user(user: schema.UserCreate, db: Session = Depends(services.get_db)):
    db_user = services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="this email already in use."
        )
    return services.create_user(db=db, user=user)


@app.post("/token", response_model=schema.Token)
def login(db: Session = Depends(services.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = services.authenticate_user(
        email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_handlers.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/", response_model=List[schema.User])
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


# Todo
@app.get("/movies/", response_model=List[schema.Movies])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(services.get_db)):
    movie_all = services.get_movies(db=db, skip=skip, limit=limit)
    return movie_all


@app.get("/movies/{movie_id}/", response_model=schema.Movies)
def read_movie(movie_id: int, db: Session = Depends(services.get_db)):
    db_movie = services.get_movie(db=db, movie_id=movie_id)

    if db_movie is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return db_movie


@app.delete("/movies/{movie_id}/")
def delete_movie(movie_id: int, db: Session = Depends(services.get_db)):
    services.delete_movie(db=db, movie_id=movie_id)
    return {"message": "seccessfully delete post with id : {movie_id}"}


@app.post("/movies/{movie_id}/comments")
def add_comment(movie_id: int, comment: schema.CommentsCreate, db: Session = Depends(services.get_db)):
    return services.add_comment(db=db, comment=comment, movie_id=movie_id)


@app.get("/relation/commentsToMovies/")
def get_relation():
    data = services.temp
    return data


@app.get("/comments/")
def get_all_comments(skip: int = 0,
                     limit: int = 100,
                     db: Session = Depends(services.get_db)):
    comments = services.get_all_comments(db=db, skip=skip, limit=limit)
    return comments

#todo testing
@app.get("/user_testing", response_model=schema.User)
def read_users_me(current_user: schema.User = Depends(get_current_user)):

    user = current_user
    return user
