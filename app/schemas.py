from pydantic import BaseModel

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