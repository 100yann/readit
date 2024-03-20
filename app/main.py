from fastapi import FastAPI
from .routers import reviews, users, books
from .database import engine
from . import models


app = FastAPI()
app.include_router(reviews.router)
app.include_router(users.router)
app.include_router(books.router)


models.Base.metadata.create_all(bind=engine)




