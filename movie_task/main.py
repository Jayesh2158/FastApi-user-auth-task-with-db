from fastapi import FastAPI
from .database import engine
from .users import models as users_models, main as users_main
from .movies_stuff import models as movies_stuff_models, main as movies_stuff_main
from . import users, movies_stuff


users_models.Base.metadata.create_all(bind=engine)
movies_stuff_models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(users_main.app)
app.include_router(movies_stuff_main.app)
