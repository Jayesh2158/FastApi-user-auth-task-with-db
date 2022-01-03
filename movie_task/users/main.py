from datetime import timedelta
import os
import uuid
from fastapi import Depends, APIRouter, HTTPException, status, File, UploadFile
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import session
from starlette.responses import JSONResponse
from movie_task import jwt_handlers
from movie_task.users import authentication
from . import schema, models, services
from ..dependencies import get_db, get_current_user
import json
from .. import emailUtils
from ..movies_stuff import services as movie_services


app = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@app.get("/testing")
def get_logined_user(current_user: models.User = Depends(get_current_user)):

    return {"user": current_user}


@app.get("/api/v1/health")
async def health_check_api(db: session.Session = Depends(get_db)):
    if db:
        return json.dumps({"healthy": True})
    return json.dumps({"healthy": False})


@app.post("/login", response_model=schema.Token)
def login(db: session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authentication.authenticate_user(
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


@app.post("/register", response_model=schema.User)
def register_user(user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = services.get_user_by_email(db=db, email=user.email)
    if db_user is not None:
        raise HTTPException(
            status_code=400, detail="this email already in use."
        )
    return services.create_user(db=db, user=user)


@app.get("/")
def get_users_data(skip: int = 0, limit: int = 100, db: session.Session = Depends(get_db)):
    users = services.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/{user_id}")
def get_user_data(user_id: int, db: session.Session = Depends(get_db)):
    db_user = services.get_user(db=db, user_id=user_id)

    if db_user is None:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )
    return db_user


@app.delete("/delete")
def hard_delete_user(db: session.Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    print(current_user.id)
    return services.delete_user(db, current_user.id)


@app.post("/reset-password")
async def reset_password(data: schema.Reset_password, db: session.Session = Depends(get_db)):
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


@app.post("/app-login")
def login_data(db: session.Session = Depends(get_db),
               current_user: models.User = Depends(get_current_user)):
    return movie_services.get_latest_movies(db=db, skip=0, limit=10)


@app.post("/profile/")
async def upload_user_photo(db: session.Session = Depends(get_db),
                            file: UploadFile = File(...),
                            current_user: models.User = Depends(
                                get_current_user)
                            ):
    cwd = os.getcwd()
    path_image_dir = "upload-images/user-profile/" + str(current_user.id) + "/"
    full_image_path = os.path.join(cwd, path_image_dir, file.filename)

    # Create directory if not exist
    if not os.path.exists(path_image_dir):
        dir = os.path.join(cwd, "upload-images")
        os.mkdir(dir)
        dir = os.path.join(cwd, "upload-images", "user-profile")
        os.mkdir(dir)
        dir = os.path.join(cwd, "upload-images",
                           "user-profile", str(current_user.id))
        os.mkdir(dir)

    # Rename file to "profile.png"
    file_name = full_image_path.replace(file.filename, "profile.png")

    # Write file
    with open(file_name, "wb+") as f:
        f.write(file.file.read())
        f.flush()
        f.close()

    # Save file in user profile database
    current_user.user_profile_image = file_name
    services.upload_profile_image(db, current_user.user_profile_image)

    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Profile image upload success",
        "profile_image": os.path.join(path_image_dir, "profile.png"),
    }


@app.post("/forgetPass")
async def forget_password(email: EmailStr, db: session.Session = Depends(get_db)):
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
