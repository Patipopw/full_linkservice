from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api.endpoints import users, quotations 
import os
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from pathlib import Path

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

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    # ถ้าเชื่อมต่อได้ จะไม่ Error และคืนค่า Success
    return {"message": "Database connection is successful!"}


app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router) 
app.include_router(quotations.router)