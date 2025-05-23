from .. import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from .auth import get_current_user
from datetime import datetime, timezone

user_router = APIRouter()

@user_router.get("/", response_model=schemas.UsersList)
def get_all_users(user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if db_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unauthorized, you are not an admin")
    
    users = db.query(models.Users).all()
    return {"users" : users}

@user_router.delete("/{user_id}")
def delete_user(user_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if db_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Admin access required")

    if db_user.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")

    user_to_delete = db.query(models.Users).filter(models.Users.user_id == user_id).first()

    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@user_router.patch("/grant/{user_id}")
def grant_admin_priv(user_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.get('sub')).first()
    if db_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Admin access required")

    user_to_grant = db.query(models.Users).filter(models.Users.user_id == user_id).first()

    if not user_to_grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_to_grant.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already an admin")
    
    user_to_grant.role = "admin"
    db.commit()
    return {"message": f"User {user_to_grant.name} has been granted admin priveleges."}