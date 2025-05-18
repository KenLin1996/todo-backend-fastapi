# routers/user.py
from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, UserLogin, UserInDB, UserOut
from models.token import TokenResponse
from auths.auth import get_current_user
from db.mongodb import db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from bson import ObjectId
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY","super-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小時

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15)) # days=7
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    existing_user = await db["users"].find_one({"email": user.email})
    existing_name = await db["users"].find_one({"name": user.name})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if existing_name:
        raise HTTPException(status_code=400, detail="Name already registered")
    
    hashed = hash_password(user.password)
    user_data = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed
    }

    result = await db["users"].insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    return UserOut(**user_data)


@router.post("/login", response_model=TokenResponse)
async def login(user:UserLogin):
    db_user = await db["users"].find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": str(db_user["_id"]), "email": db_user["email"]}
    token = create_access_token(token_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: UserInDB = Depends(get_current_user)):
    return UserOut(id=current_user.id, email=current_user.email, name=current_user.name)
    