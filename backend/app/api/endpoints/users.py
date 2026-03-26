from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.api.auth import get_current_user
from app.schemas.user import UserUpdate, UserOut, UserRoleUpdate
from app.crud.user import update_user_roles, get_users_with_roles
from app.dependencies.auth import PermissionChecker
from app.models.user import User
from typing import List

router = APIRouter()

@router.put("/{user_id}/roles", response_model=UserOut)
def api_update_user_roles(user_id: int, data: UserRoleUpdate, db: Session = Depends(get_db)):

    updated_user = update_user_roles(db, user_id=user_id, role_ids=data.role_ids)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return updated_user

@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # มั่นใจว่าเฉพาะ Admin ที่เข้าถึงหน้านี้ได้
    _: User = Depends(PermissionChecker("manage_users"))
):
    """
    API สำหรับดึงรายชื่อผู้ใช้ทั้งหมดพร้อมสิทธิ์ (สำหรับหน้า Dashboard)
    """
    users = get_users_with_roles(db, skip=skip, limit=limit)
    return users