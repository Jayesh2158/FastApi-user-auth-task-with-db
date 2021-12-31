from sqlalchemy.orm import session
from . import models
from movie_task import jwt_handlers


def authenticate_user(email: str, password: str, db: session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not jwt_handlers.verify_password(password, user.hashed_password):
        return None
    return user
