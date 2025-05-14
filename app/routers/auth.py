from .. import schemas, models
from ..config import settings
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response, Request
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime,timedelta, timezone

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
password_context = CryptContext(schemes=[settings.PASS_HASH], deprecated='auto')

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
    hashed_password = password_context.hash(user.password)
    new_user = models.Users(name=user.name, hashed_password=hashed_password, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    
@auth_router.post('/login')
def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    login_user = db.query(models.Users).filter(models.Users.email == user.username).first()
    verified = password_context.verify(user.password, login_user.hashed_password)
    if not login_user or not verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={'sub':user.username, 'role':login_user.role}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': access_token,'token_type':'bearer'}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@auth_router.get('/user', response_model=schemas.UserRead)
def get_user_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = db.query(models.Users).filter(models.Users.email == email).first()
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@auth_router.get('/verify_token')
async def verify_token(token: str = Depends(oauth2_scheme)):
    payload = get_current_user(token=token)
    return {"email":payload.get('sub')}