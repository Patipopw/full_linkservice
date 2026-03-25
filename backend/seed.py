from sqlalchemy.orm import Session
from app.db.session import SessionLocal 
from app.models.user import User
from app.models.auth import Role, Permission
from app.core.security import Hasher

def seed_data():
    db = SessionLocal()
    try:
        # 1. สร้าง Permissions พื้นฐาน
        perms_list = [
            {"name": "view_quotation", "desc": "ดูใบเสนอราคา"},
            {"name": "create_quotation", "desc": "สร้างใบเสนอราคา"},
            {"name": "edit_quotation", "desc": "แก้ไขใบเสนอราคา"},
            {"name": "delete_quotation", "desc": "ลบใบเสนอราคา (Soft Delete)"},
            {"name": "manage_users", "desc": "จัดการผู้ใช้และสิทธิ์"},
        ]
        
        db_perms = {}
        for p in perms_list:
            perm = db.query(Permission).filter(Permission.name == p["name"]).first()
            if not perm:
                perm = Permission(name=p["name"], description=p["desc"])
                db.add(perm)
                db.flush() # เพื่อให้ได้ id มาใช้ต่อ
            db_perms[p["name"]] = perm

        # 2. สร้าง Roles
        # Role: Admin (ได้ทุกสิทธิ์)
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="ผู้ดูแลระบบสูงสุด")
            admin_role.permissions = list(db_perms.values())
            db.add(admin_role)

        # Role: Sale (สร้างและดูได้)
        sale_role = db.query(Role).filter(Role.name == "sale").first()
        if not sale_role:
            sale_role = Role(name="sale", description="พนักงานขาย")
            sale_role.permissions = [db_perms["view_quotation"], db_perms["create_quotation"]]
            db.add(sale_role)

        db.flush()

        # 3. สร้าง Admin User ตัวแรก
        admin_user = db.query(User).filter(User.email == "linkservice@example.com").first()
        if not admin_user:
            admin_user = User(
                email="linkservice@example.com",
                hashed_password=Hasher.get_password_hash("En1supp@rt"), 
                full_name="System Admin",
                is_active=True
            )
            admin_user.roles.append(admin_role)
            db.add(admin_user)

        db.commit()
        print("✅ Seed data completed successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
