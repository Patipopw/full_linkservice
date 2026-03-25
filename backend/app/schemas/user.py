from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List


class RoleOut(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)
# สำหรับรับข้อมูลตอน Register
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# สำหรับส่งข้อมูล User กลับไป (Next.js จะใช้ค่านี้)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None  
    nickname: Optional[str] = None  
    is_active: bool
    roles: List[RoleOut] = [] 

    class Config:
        from_attributes = True  # ช่วยให้แปลงจาก SQLAlchemy Model เป็น Pydantic ได้อัตโนมัติ

# สำหรับส่ง Token กลับไปหลัง Login สำเร็จ
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# สำหรับข้อมูลที่ฝังอยู่ใน Token (Payload)
class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    tel: Optional[str] = None
    position: Optional[str] = None

class UserUpdate(UserBase):
    # ใช้สำหรับรับค่าตอน Update (ทุกอย่างเป็น Optional)
    pass

class UserRoleUpdate(BaseModel):
    role_ids: List[int]  