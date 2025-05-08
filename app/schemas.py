from pydantic import BaseModel, EmailStr
from datetime import datetime

class ProductBaseSchema(BaseModel):
    product_id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    imgURL: str | None = None

    class Config:
        from_attributes = True

class NewProduct(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    imgURL: str | None = None

class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    class config:
        from_attributes = True
    
class OrderBaseSchema(BaseModel):
    order_id: int
    user_id: int
    total_price: float
    status: str
    order_date: datetime
    delivery_date: datetime | None = None

    class Config:
        from_attributes = True

class OrderItemBaseSchema(BaseModel):
    product_id: int
    quantity: int

class NewOrder(BaseModel):
    order_items: list[OrderItemBaseSchema]

    class Config:
        from_attributes = True