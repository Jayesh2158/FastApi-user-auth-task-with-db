# import database as _database
# from sqlalchemy import engine
import sqlalchemy.orm as _orm
from sqlalchemy.orm.session import Session

from movie_task import schema
from . import models
from .database import engine , SessionLocal

def create_database():
    return models.Base.metadata.create_all(bind=engine) #bind=engine

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally : 
        db.close()

def get_users(db:Session,skip:int,limit:int):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_email(db: _orm.Session, email:str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: _orm.Session, user:schema.UserCreate):
    fake_hashed_password = user.password + "thisisnotsecure"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user