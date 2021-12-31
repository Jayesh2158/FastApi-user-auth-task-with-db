from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose.exceptions import JWEError
from sqlalchemy.orm.session import Session
from .database import SessionLocal
from . import jwt_handlers
import fastapi
import jwt
from .users import models, schema


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
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
