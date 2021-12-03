import enum
import json
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Form, File, UploadFile
from jose.exceptions import JWEError
from pydantic.networks import EmailStr
from starlette.responses import JSONResponse
from . import schema, services, jwt_handlers, models, emailUtils
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

services.create_database()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
        models.User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/user_testing")
def get_logined_user(current_user: models.User = Depends(get_current_user)):

    return {"user": current_user}


@app.get("/api/v1/health")
async def health_check_api(db: Session = Depends(services.get_db)):
    if db:
        return json.dumps({"healthy": True})
    return json.dumps({"healthy": False})


@app.post("/token", response_model=schema.Token)
@app.post("/login", response_model=schema.Token)
def login(db: Session = Depends(services.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = services.authenticate_user(
        email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(
        minutes=jwt_handlers.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_handlers.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users", response_model=schema.User)
def register_user(user: schema.UserCreate, db: AsyncSession = Depends(services.get_db)):
    db_user = services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="this email already in use."
        )
    return services.create_user(db=db, user=user)


@app.get("/users")
def get_users_data(skip: int = 0, limit: int = 100, db: Session = Depends(services.get_db)):
    users = services.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}")
def get_user_data(user_id: int, db: Session = Depends(services.get_db)):
    db_user = services.get_user(db=db, user_id=user_id)

    if db_user is None:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )
    return db_user


@app.post("/users/movies", response_model=schema.Movies)
def add_user_movie(movie: schema.MoviesCreate, db: Session = Depends(services.get_db),
                   current_user: models.User = Depends(get_current_user)):

    db_user = services.get_user(db=db, user_id=current_user.id)

    if db_user is None:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )

    return services.create_movie(db=db, movie=movie, user_id=current_user.id)


@app.get("/movies")
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(services.get_db)):
    movie_all = services.get_movies(db=db, skip=skip, limit=limit)
    return movie_all


@app.get("/movies/{movie_id}")
def get_movie_detail(movie_id: int, db: Session = Depends(services.get_db)):
    db_movie = services.get_movie(db=db, movie_id=movie_id)

    if db_movie is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return db_movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(services.get_db)):
    services.delete_movie(db=db, movie_id=movie_id)

    return {"message": f"seccessfully delete movie with id: {movie_id}"}


@app.put("/movies/{movie_id}", response_model=schema.Movies)
def edit_movie_data(movie_id: int, movie: schema.MoviesCreate, db: Session = Depends(services.get_db)):
    result = services.update_movie_detail(
        db=db, movie=movie, movie_id=movie_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return result


@app.post("/movies/{movie_id}/comments")
def add_comment_to_movie(movie_id: int, comment: schema.CommentsCreate, db: Session = Depends(services.get_db)):
    result = services.add_comment(db=db, comment=comment, movie_id=movie_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail="movie does not exist"
        )
    return result


@app.get("/latest/movies")
def get_recently_added_movies(skip: int = 0, limit: int = 100, db: Session = Depends(services.get_db)):
    result = services.get_latest_movies(db=db, skip=skip, limit=limit)
    return result


class GenreType(str, enum.Enum):
    comedy = "comedy"
    sic_fic = "sic-fic"
    string = "string"
    action = "action"


@app.get("/actions/movie")
def get_movies_by_action(genre: GenreType, db: Session = Depends(services.get_db), year: int = 0, skip: int = 0, limit: int = 100):
    return services.movies_by_action(db=db, year=year, genre=genre, skip=skip, limit=limit)


@app.get("/search")
def search_movie_api(data: str, db: Session = Depends(services.get_db), skip: int = 0, limit: int = 100):
    return services.blind_search(db=db, limit=limit, skip=skip, data=data)


@app.post("/forgetPass")
async def forget_password(email: EmailStr, db: Session = Depends(services.get_db)):
    user = services.get_user_by_email(db=db, email=email)
    if user is None:
        raise HTTPException(
            status_code=404, detail="this user does not exist"
        )
    reset_code = str(uuid.uuid1())
    services.create_reset_code(email, reset_code, db)
    subject = "Hello Coder"
    recipient = [email]
    message = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Reset Password</title>
    </head>
    <body>
    <a href="http://127.0.0.1:8000/user/forgot-password?reset_password_token={}">Pass-Reset-link</a>
    </body>
    </html>""".format(reset_code)
    await emailUtils.send_mail(subject, recipient, message)
    return JSONResponse(status_code=200, content={"reset_code": reset_code, "message": "email has been sent"})


@app.post("/files/")
async def create_file(
    file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


@app.post("/app-login")
def login_data(db: Session = Depends(services.get_db),
               current_user: models.User = Depends(get_current_user)):
    return services.get_latest_movies(db=db, skip=0, limit=10)


@app.post("/reset-password")
async def reset_password(data: schema.Reset_password, db: Session = Depends(services.get_db)):
    black_list_token = services.black_list_check(db=db, token=data.reset_token)
    if black_list_token is not None:
        raise HTTPException(
            status_code=404, detail="Not Found"
        )
    expire_check = services.token_expire_check(db=db, token=data.reset_token)
    if expire_check:
        raise HTTPException(
            status_code=404, detail="Not Found"
        )
    if data.password != data.confirm_password:
        if expire_check:
            raise HTTPException(
                status_code=400, detail="Not Request"
            )
    return services.reset_user_password(db=db, data=data)