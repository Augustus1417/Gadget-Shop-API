from .. import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from .auth import get_current_user

address_router = APIRouter()

@address_router.post('/')
def new_address(payload: schemas.NewAddress, user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_address = models.Addresses(user_id=db_user.user_id, address=payload.address)
    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return {'message': "Address successfully added!"}

@address_router.get('/user', response_model=schemas.UserAddresses)
def get_user_addresses(user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    addresses = db.query(models.Addresses).filter(models.Addresses.user_id == db_user.user_id).all()

    if not addresses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no addresses")
    
    return {"addresses": addresses}

@address_router.delete('/delete/{address_id}')
def delete_address(address_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    address = db.query(models.Addresses).filter(models.Addresses.user_id == db_user.user_id, models.Addresses.address_id == address_id).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.flush()
    db.commit()
    return {'detail': "Address deleted successfully"}