from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user  
from app.models.user import User
from app.models.auth import Role

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)):
        # ตรวจสอบ Permissions ทั้งหมดที่ User มีผ่านทุึก Roles
        user_permissions = {
            perm.name 
            for role in current_user.roles 
            for perm in role.permissions
        }
        
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {self.required_permission}"
            )
        
        return current_user
