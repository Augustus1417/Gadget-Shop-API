from sqlalchemy import Integer, String, Column, ForeignKey, Float, Text, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone
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

    order_items = relationship("Order_Items", back_populates="product")
    cart = relationship("Cart", back_populates="product")

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(60), nullable=False)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(5), default="user")

    orders = relationship("Orders", back_populates="user")
    cart = relationship("Cart", back_populates="user")
    addresses = relationship("Addresses", back_populates="user")

class OrderStatus(enum.Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    cancelled= "cancelled"

class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    address = Column(Text, nullable=True)
    order_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    delivery_date = Column(DateTime, nullable=True)

    user = relationship("Users", back_populates="orders")
    order_items = relationship("Order_Items", back_populates="order")

class Order_Items(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE')) 
    quantity = Column(Integer, nullable=False)
    order_price = Column(Float, nullable=False)

    order = relationship("Orders", back_populates="order_items")
    product = relationship("Products", back_populates="order_items")

class Cart(Base):
    __tablename__ = 'cart'

    cart_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'))
    quantity = Column(Integer, nullable=False)

    product = relationship("Products", back_populates="cart")
    user = relationship("Users", back_populates="cart")

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='unique_cart_item'),
    )

class Addresses(Base):
    __tablename__ = "addresses"

    address_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    address = Column(Text, nullable=False)

    user = relationship("Users", back_populates="addresses")