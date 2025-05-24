from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

DATABASE_URI = f"mysql+pymysql://{settings.USERNAME}:{settings.PASSWORD}@{settings.HOSTNAME}/{settings.DATABASE}"

engine = create_engine (DATABASE_URI, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: db.close()