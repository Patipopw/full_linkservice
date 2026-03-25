from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM
import os
from app.models.auth import Role

# บอก FastAPI ว่าจะไปหา Token ที่ไหน (ใน Header Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # ดึง User พร้อมกับ Roles และ Permissions ทั้งหมดใน Query เดียว (Eager Loading)
    user = db.query(User).options(
        joinedload(User.roles).joinedload(Role.permissions)
    ).filter(User.email == email).first()

    if user is None:
        raise credentials_exception
    
    # เช็คว่า Account ยังเปิดใช้งานอยู่หรือไม่
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user
