import hashlib
import json
import time
import httpx
from fastapi import status, HTTPException, Request
from app.core.config import settings 
from pydantic import BaseModel

def verify_hash(request: Request, trc_model: dict) -> bool:
    """ ตรวจสอบ Hash MD5 โดยใช้ค่าจาก Settings """
    actual_path = request.url.path
    
    t_time = trc_model.get('time', '')
    t_id = trc_model.get('id', '')
    t_comp = trc_model.get('company_id', '')
    received_hash = trc_model.get('hash', '')

    check_input = f"{settings.TRC_ORIGIN}{actual_path}t{t_time}{t_id}{t_comp}"
    
    expected_hash = hashlib.md5(check_input.encode('utf-8')).hexdigest()
    return expected_hash.lower() == received_hash.lower()

async def trcloud_api_read(document: str, id_value: int):
    """ ฟังก์ชันดึงข้อมูล (Read) จาก TRCloud โดยใช้ Pydantic Settings """
    timestamp = int(time.time())
    
    # คำนวณ Secure Key โดยใช้ TRC_ENCRYPT_HEAD จาก settings
    hash_input = f"{settings.TRC_ENCRYPT_HEAD}t{timestamp}"
    hash_result = hashlib.md5(hash_input.encode('utf-8')).hexdigest()

    payload = {
        "company_id": settings.TRC_COMPANY_ID,
        "passkey": settings.TRC_PASSKEY,
        "securekey": hash_result,
        "timestamp": timestamp,
        "id": id_value
    }
    
    data = {'json': json.dumps(payload)}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": settings.TRC_ORIGIN
    }

    async with httpx.AsyncClient() as client:
        try:
            # ใช้ TRC_API_BASE_URL จาก settings
            url = f"{settings.TRC_API_BASE_URL}/{document}/read.php"
            
            response = await client.post(url, data=data, headers=headers, timeout=15.0)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"TRCloud API error: {exc.response.text}"
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"TRCloud connection failed: {str(exc)}"
            )

