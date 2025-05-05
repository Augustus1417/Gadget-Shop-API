from fastapi import FastAPI
from .routers.products import product_router
from .routers.auth import auth_router
from . import models
from .database import engine
from .config import Settings
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = Settings.CORS_ORIGINS.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)

app.include_router(auth_router,tags=['Authentication'], prefix='/api/auth')
app.include_router(product_router,tags=['Products'], prefix='/api/products')
