from fastapi import FastAPI
from .routers.products import router
from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router,tags=['Products'], prefix='/api/products')
