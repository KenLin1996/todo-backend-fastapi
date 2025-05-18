# auth/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.user import UserInDB
from db.mongodb import db
from bson import ObjectId
import os

SECRIT_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRIT_KEY, algorithms=[ALGORITHM])
        user_id : str = payload.get("sub")
        if user_id is None:
            raise credentials_exception    
    except JWTError:
        raise credentials_exception

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise credentials_exception
    
    return UserInDB(id=str(user["_id"]), name=user["name"],email=user["email"], hashed_password=user["hashed_password"])