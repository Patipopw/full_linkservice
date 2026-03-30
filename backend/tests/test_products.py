def test_search_product(client):
    # 1. ลองค้นหาคำว่า "เหล็ก" (ซึ่งใน DB ยังว่างอยู่)
    response = client.get("/api/v1/products/search?q=เหล็ก")
    assert response.status_code == 200
    assert response.json() == []  # ควรได้ลิสต์ว่าง

def test_create_product_and_search(client):
    # ทดสอบว่าถ้ามีข้อมูลแล้ว ค้นหาต้องเจอ
    # (ต้องเขียนฟังก์ชันเติมข้อมูลจำลองใน conftest ก่อน)
    pass