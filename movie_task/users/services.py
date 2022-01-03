from fastapi.exceptions import HTTPException
from . import models, schema
import sqlalchemy.orm as _orm
from sqlalchemy.orm.session import Session
from .. import jwt_handlers
from sqlalchemy.orm import joinedload
import datetime


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


def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"detail": "successfull deleted"}


def create_reset_code(email: str, reset_code: str, db: Session):
    new_code = models.Forgotpass_code(
        reset_code=reset_code, email=email)
    db.add(new_code)
    db.commit()
    db.refresh(new_code)


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


def black_list_check(db: Session, token: str):
    return db.query(models.Black_list).filter(models.Black_list.token == token).first()


def token_expire_check(db: Session, token: str):
    fetch_token = db.query(models.Forgotpass_code).filter(
        models.Forgotpass_code.reset_code == token).first()
    if fetch_token.expired_in - datetime.datetime.now() >= datetime.timedelta(minutes=10):
        return True
    return False
