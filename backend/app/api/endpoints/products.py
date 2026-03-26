from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.product import Product as ProductSchema
from app.schemas.product import ProductCreate
from app.crud.product import search_products, sync_external_product, sync_multiple_products, get_products, count_products, update_product_status, crud_soft_delete_product

router = APIRouter()

@router.get("/", response_model=dict)
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
):
    items = get_products(
        db, skip=skip, limit=limit, category=category, is_active=is_active, search=search
    )
    total = count_products(db, category=category, is_active=is_active)
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/search", response_model=List[ProductSchema])
async def search_product_master(
    q: str = Query(None, min_length=1, description="ค้นหาจากชื่อหรือ SKU"),
    db: Session = Depends(get_db)
):
    """
    API สำหรับ Search/Autocomplete เพื่อใช้ในหน้าสร้างใบเสนอราคา
    """
    return search_products(db, query=q)

@router.post("/sync", response_model=ProductSchema)
def sync_single_product(obj_in: ProductCreate, db: Session = Depends(get_db)):
    """ อัปเดตหรือสร้างสินค้าใหม่ทีละรายการ """
    return sync_external_product(db, product_in=obj_in)

@router.post("/sync-bulk", response_model=List[ProductSchema])
def sync_bulk_products(objs_in: List[ProductCreate], db: Session = Depends(get_db)):
    """ อัปเดตหรือสร้างสินค้าใหม่ครั้งละหลายรายการ (Batch Update) """
    return sync_multiple_products(db, products_in=objs_in)

@router.patch("/{product_id}/status", response_model=ProductSchema)
def toggle_product_status(
    product_id: int,
    is_active: bool = Body(..., embed=True), # รับค่า {"is_active": true/false} จาก Body
    db: Session = Depends(get_db)
):
    """
    Endpoint สำหรับเปิดหรือปิดการใช้งานสินค้า
    """
    db_product = update_product_status(db, product_id=product_id, is_active=is_active)
    
    if not db_product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้าที่ต้องการอัปเดต")
        
    return db_product

@router.delete("/{product_id}", response_model=ProductSchema)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    # current_user = Depends(PermissionChecker("admin_product")) 
):
    """
    ลบสินค้าออกจากระบบ (Soft Delete)
    """
    db_product = crud_soft_delete_product(db, product_id=product_id)
    
    if not db_product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้าที่ต้องการลบ หรือถูกลบไปแล้ว")
        
    return db_product

