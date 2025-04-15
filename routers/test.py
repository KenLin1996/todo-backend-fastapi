from fastapi import APIRouter
from db.mongodb import db

router = APIRouter()


@router.get("/test-db")
async def test_db():
    collections = await db.list_collection_names()
    return {"collections": collections}


@router.post("/test-insert")
async def test_insert():
    result = await db["todos"].insert_one({"title": "First Todo", "completed": False})
    return {"inserted_id": str(result.inserted_id)}
