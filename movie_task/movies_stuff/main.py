import enum
from ..dependencies import get_current_user, get_db
from fastapi import APIRouter, HTTPException, Depends
from . import schema, services
from sqlalchemy.orm import Session
from ..users import models as user_models
from ..users import services as user_service


app = APIRouter(
    prefix="/movies",
)


@app.post("/", response_model=schema.Movies)
def add_user_movie(movie: schema.MoviesCreate, db: Session = Depends(get_db),
                   current_user: user_models.User = Depends(get_current_user)):

    db_user = user_service.get_user(db=db, user_id=current_user.id)

    if db_user is None:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )

    return services.create_movie(db=db, movie=movie, user_id=current_user.id)


@app.get("/")
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movie_all = services.get_movies(db=db, skip=skip, limit=limit)
    return movie_all


@app.get("/{movie_id}")
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    db_movie = services.get_movie(db=db, movie_id=movie_id)

    if db_movie is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return db_movie


@app.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    services.delete_movie(db=db, movie_id=movie_id)

    return {"message": f"seccessfully delete movie with id: {movie_id}"}


@app.put("/{movie_id}", response_model=schema.Movies)
def edit_movie_data(movie_id: int, movie: schema.MoviesCreate, db: Session = Depends(get_db)):
    result = services.update_movie_detail(
        db=db, movie=movie, movie_id=movie_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return result


@app.post("/{movie_id}/comments")
def add_comment_to_movie(movie_id: int, comment: schema.CommentsCreate, db: Session = Depends(get_db)):
    result = services.add_comment(db=db, comment=comment, movie_id=movie_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return result


@app.get("/latest")
def get_recently_added_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = services.get_latest_movies(db=db, skip=skip, limit=limit)
    return result


class GenreType(str, enum.Enum):
    comedy = "comedy"
    sic_fic = "sic-fic"
    string = "string"
    action = "action"


@app.get("/actions")
def get_movies_by_action(genre: GenreType, db: Session = Depends(get_db), year: int = 0, skip: int = 0, limit: int = 100):
    return services.movies_by_action(db=db, year=year, genre=genre, skip=skip, limit=limit)


@app.get("/search")
def search_movie_api(data: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return services.blind_search(db=db, limit=limit, skip=skip, data=data)
