from datetime import timedelta
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import session
from . import models
from movie_task import jwt_handlers
from fastapi import APIRouter, Depends
from . import schema
from ..dependencies import get_db


app = APIRouter(
    tags=["For_Authorize"]
)


def authenticate_user(email: str, password: str, db: session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not jwt_handlers.verify_password(password, user.hashed_password):
        return None
    return user


@app.post("/token", response_model=schema.Token)
def login(db: session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
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
