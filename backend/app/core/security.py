from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import os
import bcrypt
from app.core.config import settings

# SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

class Hasher:

  @staticmethod
  def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

  @staticmethod
  def get_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=1440)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)