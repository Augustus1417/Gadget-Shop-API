from pydantic import BaseModel, EmailStr

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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    class config:
        from_attributes = True