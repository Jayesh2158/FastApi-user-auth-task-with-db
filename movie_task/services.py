import datetime
from fastapi.exceptions import HTTPException
import sqlalchemy.orm as _orm
from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session
from movie_task import schema
from . import models, jwt_handlers
from .database import engine, SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import or_


def create_database():
    return models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users(db: Session, skip: int, limit: int):
    return db.query(models.User).options(joinedload(models.User.movies)).offset(skip).limit(limit).all()


def get_user_by_email(db: _orm.Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: _orm.Session, user: schema.UserCreate):
    hash_password = jwt_handlers.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, hashed_password=hash_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).options(joinedload(models.User.movies)).first()


def create_movie(db: Session, movie: schema.MoviesCreate, user_id: int):
    new_movie = models.Movies(**movie.dict(), owner_id=user_id)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie


def get_movies(db: Session, skip: int, limit: int):
    return db.query(models.Movies).options(joinedload(models.Movies.comment)).offset(skip).limit(limit).all()


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movies).filter(models.Movies.id == movie_id).first() # options(joinedload(models.Movies.comment)).first()


def delete_movie(db: Session, movie_id: int):
    movie = get_movie(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    db.query(models.Movies).filter(models.Movies.id == movie_id).delete()
    db.query(models.Comments).filter(
        models.Comments.movie_id == movie_id).delete()
    db.commit()


def add_comment(db: Session, movie_id: int, comment: schema.CommentsCreate):
    movie = get_movie(db=db, movie_id=movie_id)
    if movie is None:
        return None
    new_comment = models.Comments(**comment.dict(), movie_id=movie_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not jwt_handlers.verify_password(password, user.hashed_password):
        return None
    return user


def update_movie_detail(db: Session, movie: schema.MoviesCreate, movie_id: int):
    selected_movie = get_movie(db=db, movie_id=movie_id)
    if selected_movie is None:
        return None
    selected_movie.name = movie.name
    selected_movie.genres = movie.genres
    selected_movie.release_year = movie.release_year
    db.commit()
    db.refresh(selected_movie)
    return selected_movie


def get_latest_movies(db: Session, skip: int, limit: int):
    result = db.query(models.Movies).order_by(models.Movies.id.desc()).options(
        joinedload(models.Movies.comment)).offset(skip).limit(limit).all()
    return result


all_genre = ['string', 'action', 'comedy', 'sic-fic']


def movies_by_action(db: Session, year: int, genre: str, skip: int, limit: int):
    if year > 0:
        if year >= 1950 and year <= 2021:
            result = db.query(models.Movies).filter(models.Movies.release_year == year).options(
                joinedload(models.Movies.comment)).offset(skip).limit(limit).all()
            if len(result) < 1:
                raise HTTPException(
                    status_code=404, detail=f"No movies found of year {year}"
                )
        else:
            raise HTTPException(
                status_code=400, detail="Invalid input"
            )
    if genre in all_genre:
        result = db.query(models.Movies).filter(models.Movies.genres == genre).options(
            joinedload(models.Movies.comment)).offset(skip).limit(limit).all()
        if len(result) < 1:
            raise HTTPException(
                status_code=404, detail=f"No movies found of genre {genre}"
            )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid Genre Input"
        )
    return result


def blind_search(db: session, data: str, limit: int, skip: int):
    movie = db.query(models.Movies).filter(or_(models.Movies.name.contains(data), models.Movies.genres.contains(
        data), models.Movies.release_year.like(data))).options(
        joinedload(models.Movies.comment)).offset(skip).limit(limit).all()

    if len(movie) < 1:
        raise HTTPException(
            status_code=404, detail="No data found"
        )
    return movie


def create_reset_code(email: str, reset_code: str, db: Session):
    new_code = models.Forgotpass_code(
        reset_code=reset_code, email=email)
    db.add(new_code)
    db.commit()
    db.refresh(new_code)


def black_list_check(db: Session, token: str):
    return db.query(models.Black_list).filter(models.Black_list.token == token).first()


def token_expire_check(db: Session, token: str):
    fetch_token = db.query(models.Forgotpass_code).filter(
        models.Forgotpass_code.reset_code == token).first()
    if fetch_token.expired_in - datetime.datetime.now() >= datetime.timedelta(minutes=10):
        return True
    return False


def reset_user_password(db: Session, data: schema.Reset_password):
    token = db.query(models.Forgotpass_code).filter(
        models.Forgotpass_code.reset_code == data.reset_token).first()
    if token is None:
        raise HTTPException(
            status_code=404, detail="No token found"
        )
    user = db.query(models.User).filter(
        models.User.email == token.email).first()
    if user is None:
        raise HTTPException(
            status_code=404, detail="No user found"
        )
    new_password = jwt_handlers.get_password_hash(data.password)
    user.hashed_password = new_password
    add_token_to_black_list = models.Black_list(token=data.reset_token)
    db.add(add_token_to_black_list)
    db.commit()
    db.refresh(user)
    return {"detail": "password reset successfully"}


def upload_profile_image(db: Session, user_image):

    db_profile_image = models.User(user_profile_image=user_image)
    db.add(db_profile_image)
    db.commit()
    db.refresh(db_profile_image)
    return db_profile_image

# Todo


def delete_user(db: Session, user_id: int):
    # s1 = db.query(models.User).filter(models.User.id == user_id).subquery()
    # db.query(models.Movies).filter(models.Movies.owner_id.in_(
    #     s1)).delete(synchronize_session='fetch')
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"detail": "successfull deleted"}
