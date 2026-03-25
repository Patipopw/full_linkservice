from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.schemas.user import UserUpdate
from app.models.auth import Role

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user_roles(db: Session, user_id: int, role_ids: list[int]):
    # ค้นหา User พร้อมโหลด Roles เดิมมาด้วย
    db_user = db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()
    
    if not db_user:
        return None

    # ค้นหา Role objects ใหม่ตามรายชื่อ IDs ที่ส่งมา
    new_roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    
    # อัปเดตความสัมพันธ์ Many-to-Many (SQLAlchemy จะจัดการตารางกลางให้เอง)
    db_user.roles = new_roles
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users_with_roles(db: Session, skip: int = 0, limit: int = 100):
    """
    ดึงรายชื่อ User ทั้งหมดพร้อม Roles (Eager Loading)
    """
    return db.query(User).options(
        joinedload(User.roles)
    ).offset(skip).limit(limit).all()