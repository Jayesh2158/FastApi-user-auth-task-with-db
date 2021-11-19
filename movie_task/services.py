import sqlalchemy.orm as _orm
from sqlalchemy.orm.session import Session

from movie_task import schema
from . import models
from .database import engine, SessionLocal


def create_database():
    return models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users(db: Session, skip: int, limit: int):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_email(db: _orm.Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: _orm.Session, user: schema.UserCreate):
    fake_hashed_password = user.password + "thisisnotsecure"
    db_user = models.User(
        email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_movie(db: Session, movie: schema.MoviesCreate, user_id: int):
    new_movie = models.Movies(**movie.dict(), owner_id=user_id)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie


def get_movies(db: Session,  skip: int, limit: int):
    return db.query(models.Movies, models.Comments).join(models.Comments).filter(models.Movies.id == models.Comments.movie_id).all()


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movies).filter(models.Movies.id == movie_id).first()


def delete_movie(db: Session, movie_id: int):
    db.query(models.Movies).filter(models.Movies.id == movie_id).delete()
    db.commit()


def add_comment(db: Session, movie_id: int, comment: schema.CommentsCreate):
    new_comment = models.Comments(**comment.dict(), movie_id=movie_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def temp(db: Session):
    return db.query(models.User, models.Movies, models.Comments).join(models.User).filter(
        models.User.id == models.Movies.owner_id).filter(models.Movies.id == models.Comments.movie_id).all()
        

def get_all_comments(db: Session, skip: int, limit: int):
    return db.query(models.Comments).offset(skip).limit(limit).all()
