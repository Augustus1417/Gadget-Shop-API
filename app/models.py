from sqlalchemy import Integer, String, Column, ForeignKey, Float, Text, Enum
from .database import Base
import enum

class ProductCategory(enum.Enum):
    phone = "phone"
    laptop = "laptop"
    accessory = "accessory"

class Products(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    stock = Column(Integer, nullable=False)
    imgURL = Column(Text, nullable=True)

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(60), nullable=False)
    hashed_password = Column(String(128), nullable=False)