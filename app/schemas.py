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
    address: str | None = None

    class Config:
        from_attributes = True

class OrderDetails(BaseModel):
    order_id: int
    user_id: int
    total_price: float
    status: str
    order_date: datetime
    delivery_date: datetime | None = None
    address: str | None = None

    class Config:
        from_attributes = True

class OrderItemBaseSchema(BaseModel):
    product_id: int
    quantity: int

class CartBaseSchema(BaseModel):
    product_id: int
    quantity:int

class NewOrder(BaseModel):
    address: str

class UserOrders(BaseModel):
    orders: list[OrderBaseSchema]

class AddressBaseSchema(BaseModel):
    address_id: int
    address: str

class NewAddress(BaseModel):
    address:str

class UserAddresses(BaseModel):
    addresses: list[AddressBaseSchema]

class ProductInfo(BaseModel):
    product_id: int
    name: str
    price: float
    imgURL: str | None = None
    category: str

    class Config:
        from_attributes = True

class OrderItemDetails(BaseModel):
    order_item_id: int
    product: ProductInfo
    quantity: int
    order_price: float

    class Config:
        from_attributes = True

class DetailedOrder(BaseModel):
    order_id: int
    user_id: int
    user_name: str | None = None  
    total_price: float
    status: str
    order_date: datetime
    delivery_date: datetime | None = None
    address: str | None = None
    order_items: list[OrderItemDetails]

    class Config:
        from_attributes = True

class DetailedUserOrders(BaseModel):
    orders: list[DetailedOrder]

class UsersInfo(BaseModel):
    user_id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class UsersList(BaseModel):
    users: list[UsersInfo]
