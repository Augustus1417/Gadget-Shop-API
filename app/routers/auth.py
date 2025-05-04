from .. import schemas, models
from ..config import settings
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta, timezone

auth_router = APIRouter()

password_context = CryptContext(schemes=[settings.PASS_HASH], deprecated='auto')

def hash_password(password: str):
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return password_context.verify(password, hashed_password)

def create_access_token(data:dict, expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+ expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return encoded_jwt

@auth_router.post('/register', response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.NewUser, db: Session = Depends(get_db)):
    new_user = db.query(models.Users).filter((models.Users.name == user.name) | (models.Users.email == user.email)).first()
    if new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name or Email is already in use")
    hashed_password = hash_password(user.password)
    new_user = models.Users(name=user.name, hashed_password=hashed_password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    
@auth_router.post('/login')
def login_user(user: schemas.UserLogin, db: Session=Depends(get_db)):
    login_user = db.query(models.Users).filter(models.Users.email == user.email).first()
    if not login_user or not verify_password(user.password, login_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={'sub':user.email}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': access_token,'token_type':'bearer'}
