from .. import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from .auth import get_current_user
from datetime import datetime, timezone

order_router = APIRouter()

@order_router.get('/', response_model=schemas.DetailedUserOrders)
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Orders).join(models.Users).options(
        joinedload(models.Orders.order_items).joinedload(models.Order_Items.product),
        joinedload(models.Orders.user)
    ).all()

    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no orders")

    detailed_orders = []
    for order in orders:
        detailed_orders.append(schemas.DetailedOrder(
            order_id=order.order_id,
            user_id=order.user_id,
            user_name=order.user.name,
            total_price=order.total_price,
            status=order.status.value,
            order_date=order.order_date,
            delivery_date=order.delivery_date,
            address=order.address,
            order_items=[
                schemas.OrderItemDetails(
                    order_item_id=item.order_item_id,
                    quantity=item.quantity,
                    order_price=item.order_price,
                    product=schemas.ProductInfo.from_orm(item.product)  # ✅ required
                ) for item in order.order_items
            ]
        ))

    return {"orders": detailed_orders}

@order_router.get('/get/{order_id}', response_model=schemas.OrderBaseSchema)
def get_order_by_id(order_id: int, db: Session=Depends(get_db)):
    order = db.query(models.Orders).filter(models.Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@order_router.get('/user/orders', response_model=schemas.DetailedUserOrders)
def get_user_orders(user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    orders = db.query(models.Orders).filter(models.Orders.user_id == db_user.user_id).all()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no orders")

    return {"orders": orders}


@order_router.post('/', response_model=schemas.OrderBaseSchema, status_code=status.HTTP_201_CREATED)
def create_order(payload: schemas.NewOrder, db: Session = Depends(get_db), user=Depends(get_current_user)):
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
        order_date = datetime.now(timezone.utc),
        address = payload.address
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

    if order.status == models.OrderStatus.cancelled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is already cancelled")

    for item in order.order_items:
        product = db.query(models.Products).filter(models.Products.product_id == item.product_id).first()
        if product:
            product.stock += item.quantity

    order.status = models.OrderStatus.cancelled  
    db.commit()
    return {"message": f"Order {order_id} has been cancelled."}

@order_router.patch('/shipped/{order_id}', status_code=status.HTTP_200_OK)
def set_to_shipped(order_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    order = db.query(models.Orders).filter(models.Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()

    if db_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unauthorized, you are not an admin")

    print(f"Before update: Order {order_id} status is {order.status}")
    
    if order.status == models.OrderStatus.pending:
        order.status = models.OrderStatus.shipped  
        db.commit()
        print(f"After update: Order {order_id} status is {order.status}")
        return {"message": f"Order {order_id} has been shipped."}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{order.status}")

@order_router.patch('/delivered/{order_id}')
def set_to_delivered(order_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    order = db.query(models.Orders).filter(models.Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()

    if db_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unauthorized, you are not an admin")

    if order.status != models.OrderStatus.delivered and order.status != models.OrderStatus.cancelled:
        order.status = models.OrderStatus.delivered  
        order.delivery_date = datetime.now(timezone.utc)  
        db.commit()
        return {"message": f"Order {order_id} has been delivered."}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{order.status}")
