import hashlib

def test_trcloud_webhook_invalid_hash(client):
    # ส่งข้อมูลแบบมั่วๆ ไป
    payload = {"id": 123, "company_id": 1, "time": 12345, "hash": "wrong_hash"}
    response = client.post("/api/v1/trcloud/webhooks/trcloud?action=create&engine=qo", data=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Hash verification failed"
