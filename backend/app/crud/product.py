from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.schemas.product import ProductCreate
from datetime import datetime

def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category: str = None, 
    is_active: bool = None,
    search: str = None
):
    """
    ดึงรายการสินค้าทั้งหมดพร้อมระบบ Pagination และ Filters
    """
    query = db.query(Product).filter(Product.deleted_at == None)

    # กรองตามหมวดหมู่
    if category:
        query = query.filter(Product.category == category)
    
    # กรองตามสถานะการใช้งาน
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    # ค้นหาเพิ่มเติม (ถ้ามีการส่งคำค้นมาพร้อมกับการดึงลิสต์)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern)
            )
        )

    # เรียงตามวันที่สร้างล่าสุด และทำ Pagination
    return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

def count_products(db: Session, category: str = None, is_active: bool = None):
    """ นับจำนวนสินค้าทั้งหมดสำหรับทำ Pagination ใน Frontend """
    query = db.query(Product).filter(Product.deleted_at == None)
    if category:
        query = query.filter(Product.category == category)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    return query.count()


def search_products(db: Session, query: str, limit: int = 20):
    """ ค้นหาสินค้าจาก SKU หรือ ชื่อ """
    return db.query(Product).filter(
        Product.is_active == True,
        Product.deleted_at == None,
        or_(
            Product.name.ilike(f"%{query}%"),
            Product.sku.ilike(f"%{query}%")
        )
    ).limit(limit).all()

def sync_external_product(db: Session, product_in: ProductCreate):
    """ อัปเดตข้อมูลถ้ามี external_id เดิม หรือสร้างใหม่ถ้าไม่มี """
    db_product = db.query(Product).filter(Product.external_id == product_in.external_id).first()
    
    if db_product:
        # Update existing
        for var, val in product_in.model_dump().items():
            setattr(db_product, var, val)
    else:
        # Create new
        db_product = Product(**product_in.model_dump())
        db.add(db_product)
    
    db.commit()
    db.refresh(db_product)
    return db_product

def sync_multiple_products(db: Session, products_in: list[ProductCreate]):
    """ สำหรับการ Sync ครั้งละหลายรายการ (Bulk Sync) """
    results = []
    for p_in in products_in:
        results.append(sync_external_product(db, p_in))
    return results

def search_products(db: Session, query: str, limit: int = 15):
    """
    ค้นหาสินค้าจากชื่อ (Name) หรือ รหัส (SKU) 
    โดยกรองเฉพาะสินค้าที่ยังใช้งานอยู่ (Active) และไม่ถูกลบ
    """
    if not query:
        return []
        
    search_pattern = f"%{query}%"
    return db.query(Product).filter(
        Product.is_active == True,
        Product.deleted_at == None,
        or_(
            Product.name.ilike(search_pattern),
            Product.sku.ilike(search_pattern),
            Product.category.ilike(search_pattern) # ค้นจากหมวดหมู่ด้วยก็ได้
        )
    ).limit(limit).all()


def update_product_status(db: Session, product_id: int, is_active: bool):
    """ อัปเดตสถานะการใช้งานของสินค้า (เปิด/ปิด) """
    db_product = db.query(Product).filter(
    	Product.id == product_id,
        Product.deleted_at == None
    ).first()
    
    if db_product:
        db_product.is_active = is_active
        db.commit()
        db.refresh(db_product)
        return db_product
    return None

def crud_soft_delete_product(db: Session, product_id: int):
    """ ลบสินค้าแบบ Soft Delete """
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.deleted_at == None
    ).first()
    
    if db_product:
        # 1. บันทึกเวลาที่ลบ
        db_product.deleted_at = datetime.now()
        
        # 2. ปิดสถานะการใช้งานพ่วงไปด้วย เพื่อความชัวร์
        db_product.is_active = False
        
        db.commit()
        db.refresh(db_product)
        return db_product
    return None
