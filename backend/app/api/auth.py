from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.models.user import User
from app.core.security import Hasher, create_access_token 
from app.schemas.user import UserCreate, UserOut, Token
from app.api.deps import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/login", response_model=Token) # เปลี่ยน dict เป็น Token
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ค้นหา User (OAuth2PasswordRequestForm จะส่ง email มาในฟิลด์ username)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # ตรวจสอบ Password ผ่าน Hasher
    if not user or not Hasher.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    user.last_login = datetime.now()
    db.commit()
    # สร้าง Token โดยใช้ email เป็น 'sub' (Subject)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, 
    "token_type": "bearer",
    "user": user
    }

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. ตรวจสอบ Email ซ้ำ
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # 2. สร้าง User และ Hash Password ผ่าน Hasher
    new_user = User(
        email=user_in.email,
        hashed_password=Hasher.get_password_hash(user_in.password),
        is_active=True
    )
    
    # 3. บันทึกลง Database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user"
        )
    

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    ดึงข้อมูลโปรไฟล์ของผู้ใช้ที่ล็อกอินอยู่
    """
    return current_user