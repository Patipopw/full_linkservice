def test_read_quotation_detail(client, seed_data):
    # 1. เรียก API
    response = client.get(f"/api/v1/quotations/{seed_data.id}")
    
    # 2. ตรวจสอบสถานะการเรียก (ควรได้ 200 OK)
    assert response.status_code == 200
    
    data = response.json()
    
    # 3. ตรวจสอบข้อมูลหลักที่ Seed ไว้
    assert data["quotation_no"] == "QO-2024-001"
    assert data["company_name"] == "My Test Company"
    assert data["customer_name"] == "Sample Customer"
    
    # เช็คว่า ID ตรงกับที่สร้างไว้จริงไหม
    assert data["id"] == seed_data.id