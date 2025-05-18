from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from .auth import get_current_user
from datetime import datetime, timezone

order_router = APIRouter()

@order_router.get('/', response_model=list[schemas.OrderBaseSchema])
def get_orders(db: Session=Depends(get_db)):
    orders = db.query(models.Orders).all()
    return orders

@order_router.get('/get/{order_id}', response_model=schemas.OrderBaseSchema)
def get_order_by_id(order_id: int, db: Session=Depends(get_db)):
    order = db.query(models.Orders).filter(models.Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@order_router.post('/', response_model=schemas.OrderBaseSchema, status_code=status.HTTP_201_CREATED)
def create_order(db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_cart = db.query(models.Cart).filter(models.Cart.user_id == db_user.user_id).all()
    if not user_cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no items in the cart")

    total_price = 0.0
    order_items_to_create = []

    for item in user_cart:
        product = db.query(models.Products).filter(models.Products.product_id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found.")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for product '{product.name}'.")

        line_total = product.price * item.quantity
        total_price += line_total
        product.stock -= item.quantity

        order_items_to_create.append(
            models.Order_Items(
                product_id=item.product_id,
                quantity=item.quantity,
                order_price=product.price 
            )
        )
        db.delete(item)

    new_order = models.Orders(
        user_id=db_user.user_id,
        total_price=total_price,
        order_date = datetime.now(timezone.utc)
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for order_item in order_items_to_create:
        order_item.order_id = new_order.order_id
        db.add(order_item)

    db.commit()
    return new_order

@order_router.patch('/cancel/{order_id}', status_code=status.HTTP_200_OK)
def cancel_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(models.Orders).filter(models.Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if order.user_id != db_user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are unauthorized to cancel this")

    if order.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is already cancelled")

    for item in order.order_items:
        product = db.query(models.Products).filter(models.Products.product_id == item.product_id).first()
        if product:
            product.stock += item.quantity

    order.status = "cancelled"
    db.commit()
    return {"message": f"Order {order_id} has been cancelled."}
