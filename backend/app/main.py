from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
# from app.api.endpoints import users, quotations 
import os
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from pathlib import Path

from app.api.api import api_router

app = FastAPI(title="Linkservice API")
origins = [
    "http://localhost:3000",    # URL ของ Next.js ตอนพัฒนา
    "https://your-domain.com",  # URL ของโปรเจกต์ตอนใช้งานจริง
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # อนุญาต Domain ใน list
    allow_credentials=True,
    allow_methods=["*"],              # อนุญาตทุก HTTP Method (GET, POST, etc.)
    allow_headers=["*"],              # อนุญาตทุก Headers
)



upload_root = Path(settings.UPLOAD_ROOT_DIR)
upload_root.mkdir(parents=True, exist_ok=True)

(upload_root / "quotations").mkdir(parents=True, exist_ok=True)
# (upload_root / "sale_orders").mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(upload_root)), name="uploads")

@app.get("/")
def read_root():
    return {"status": "Backend is running!"}

@api_router.get("/healthcheck", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        # ส่งคำสั่งง่ายๆ ไปเช็คว่า DB ยังตอบสนองไหม
        db.execute(text("SELECT 1"))
        return {
            "status": "online",
            "database": "connected",
            "message": "Service is running smoothly"
        }
    except Exception as e:
        # ถ้าเชื่อมต่อไม่ได้ ให้ส่ง Error 503 (Service Unavailable)
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


app.include_router(api_router, prefix="/api/v1")


app.include_router(auth.router, tags=["Authentication"])
# app.include_router(users.router) 
# app.include_router(quotations.router)