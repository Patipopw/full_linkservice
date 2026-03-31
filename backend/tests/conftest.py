import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models.base import Base
from fastapi.testclient import TestClient
from app.models.quotation import Quotation
from app.models.trcloud_doc import MaterialRequest, SaleOrder
from datetime import date, timedelta, datetime
from app.api.deps import get_current_user
from types import SimpleNamespace
from app.core.config import settings


import os
from dotenv import load_dotenv
load_dotenv()
# ใช้ SQLite หรือ Postgres แยกต่างหากสำหรับ Test
# SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://user:pass@localhost:5432/test_db_default")
SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    # สร้างตารางใหม่ทั้งหมดก่อนเริ่ม Test
    Base.metadata.create_all(bind=engine)
    
    mock_permission = SimpleNamespace(name="view_quotation")
    mock_role = SimpleNamespace(
        name="admin",
        permissions=[mock_permission] 
    )

    mock_user = SimpleNamespace(
        id=1,
        email="test@example.com",
        username="testadmin",
        is_active=True,
        roles=[mock_role] 
    )
    
     # 2. ฟังก์ชัน Mock ที่จะถูกเรียกแทน get_current_user จริง
    def mock_get_current_user_override():
        return mock_user

    # 3. สั่ง Override
    app.dependency_overrides[get_current_user] = mock_get_current_user_override
    

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            
    # แทนที่ get_db จริงด้วยตัวจำลอง (Mock)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
        
    # ลบตารางทิ้งหลังจบ Test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """สร้าง Database Session สำหรับใช้เติมข้อมูลโดยตรง"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def seed_data(db_session):
    """ฟังก์ชันสำหรับเติมข้อมูล Quotation และ MaterialRequest จำลอง"""
    # 1. สร้าง Quotation (ตัวแม่)
    new_quotation = Quotation(
        # --- ฟิลด์ที่ห้ามเป็น Null (nullable=False) ---
        quotation_no="QO-2024-001",
        version=0,
        company_name="My Test Company",
        customer_name="Sample Customer",
        validity_date=date.today() + timedelta(days=30), # ต้องใช้ date object
        sale_name="Test Seller",
        creator="Test Admin",
        creator_id="USR-001", # เพิ่มตัวนี้
        sale_id="SALE-001",    # เพิ่มตัวนี้
        
        # --- ฟิลด์ที่มี default อยู่แล้ว (ใส่หรือไม่ใส่ก็ได้ แต่ใส่ไว้ชัวร์กว่า) ---
        status="DRAFT",
        discount=0.00,
        vat=7.00,
        total_amount=0.00,
        sync_status="pending",
        project_name="Test Project A"
    )
    db_session.add(new_quotation)
    db_session.flush() # เพื่อให้ได้ ID ของ quotation มาใช้ต่อ

    new_so = SaleOrder(
        trcloud_id="TR-SO-999",
        company_format="STD",
        document_number="SO-2024-001",
        quotation_id=new_quotation.id  # เชื่อมกับ Quotation
    )
    db_session.add(new_so)
    db_session.commit()

    return new_quotation