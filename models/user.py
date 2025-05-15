# models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# 使用者註冊時傳入的資料格式
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 使用者登入時傳入的資料格式
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 回傳給前端的使用者資料（可選擇性回傳 id 或 email）
class UserOut(BaseModel):
    id: str
    email: EmailStr


# 若有需要內部使用的完整資料格式（例如包含雜湊密碼）
class UserInDB(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    