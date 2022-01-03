from fastapi import FastAPI
from .database import engine
from .users import models as users_models, main as users_main, authentication as user_authentication
from .movies_stuff import models as movies_stuff_models, main as movies_stuff_main


users_models.Base.metadata.create_all(bind=engine)
movies_stuff_models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(users_main.app)
app.include_router(movies_stuff_main.app)
app.include_router(user_authentication.app)
