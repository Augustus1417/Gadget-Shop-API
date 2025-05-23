from .. import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from .auth import get_current_user

cart_router = APIRouter()

@cart_router.post("/")
def add_to_cart(payload: schemas.CartBaseSchema,user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    cart_item = db.query(models.Cart).filter_by(user_id=db_user.user_id, product_id=payload.product_id).first()
    if cart_item:
        cart_item.quantity += payload.quantity
    else:
        cart_item = models.Cart(
            user_id=db_user.user_id,
            product_id=payload.product_id,
            quantity=payload.quantity
        )

    db.add(cart_item)
    db.commit()
    return {"detail": "Items added succesfully"}

@cart_router.get('/user')
def get_user_cart(user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    cart = db.query(models.Cart).options(joinedload(models.Cart.product)).filter(models.Cart.user_id == db_user.user_id).all()

    cart_data = []
    for item in cart:
        cart_data.append({
            "cart_id": item.cart_id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "product_price": item.product.price,
            "quantity": item.quantity,
            "total": item.product.price * item.quantity
        })

    return cart_data

@cart_router.delete('/delete/{cart_id}')
def delete_cart(cart_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    cart = db.query(models.Cart).filter(
        models.Cart.cart_id == cart_id,
        models.Cart.user_id == db_user.user_id ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    print("Deleting cart:", cart.cart_id, cart.user_id)
    db.delete(cart)
    db.flush()
    db.commit()
    return {'detail': "Cart deleted successfully"}