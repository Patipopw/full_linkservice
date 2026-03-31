from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
# from dotenv import load_dotenv
from app.models.base import Base
from app.core.config import settings

# load_dotenv()
DATABASE_URL = settings.DATABASE_URL
if not settings.DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg://username:password@127.0.0.1:5432/db_linkservice"

# สำหรับ PostgreSQL ปกติ
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency สำหรับใช้ใน FastAPI Endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
