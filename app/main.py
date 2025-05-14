from fastapi import FastAPI
from .routers.products import product_router
from .routers.auth import auth_router
from .routers.orders import order_router
from .routers.cart import cart_router
from . import models
from .database import engine
from .config import Settings
from fastapi.middleware.cors import CORSMiddleware

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

settings = Settings()
origins = settings.CORS_ORIGINS.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)

app.include_router(auth_router,tags=['Authentication'], prefix='/api/auth')
app.include_router(product_router,tags=['Products'], prefix='/api/products')
app.include_router(order_router,tags=['Orders'], prefix='/api/orders')
app.include_router(cart_router,tags=['Cart'], prefix='/api/cart')
