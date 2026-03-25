from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from typing import Optional
import os

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Link Service API"
    VERSION: str = "1.0.0"

    # --- Database (Pydantic จะเช็คว่าเป็นรูปแบบ URL ที่ถูกต้องไหม) ---
    DATABASE_URL: str 

    # --- Auth & Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # --- File Uploads ---
    UPLOAD_ROOT_DIR: str = "uploads"
    
    # URL พื้นฐานของ Backend (เช่น http://localhost:8000)
    BACKEND_HOST: str = "http://localhost:8000"

    # สร้าง URL สำหรับเข้าถึงไฟล์ผ่าน Browser อัตโนมัติ
    @computed_field
    @property
    def UPLOAD_URL(self) -> str:
        return f"{self.BACKEND_HOST}/uploads"

    # --- บอกให้ Pydantic อ่านไฟล์ .env ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # ถ้าใน .env มีตัวแปรเกินมาให้ข้ามไป
    )

# สร้าง Instance เพื่อเรียกใช้งานทั้งโปรเจกต์
settings = Settings()
