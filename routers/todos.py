# routers/todos.py
from fastapi import APIRouter, HTTPException
from db.mongodb import db
from bson import ObjectId
from models.todo import TodoCreate, EditTodo


router = APIRouter()


def convert_id(todo):
    todo["id"] = str(todo["_id"])
    del todo["_id"]
    return todo


@router.get("/todos")
async def get_todos():
    todos = await db["todos"].find().to_list(100)
    return [convert_id(todo) for todo in todos]


@router.post("/todos")
async def create_tod(todo: TodoCreate):
    result = await db["todos"].insert_one(todo.dict())
    new_todo = await db["todos"].find_one({"_id": result.inserted_id})
    return [convert_id(new_todo)]


@router.patch("/todos/edit/{todo_id}")
async def edit_todo(todo_id: str, todo_edit: EditTodo):
    update_data = {k: v for k, v in todo_edit.dict().items() if v is not None}
    result = await db["todos"].update_one({"_id": ObjectId(todo_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo = await db["todos"].find_one({"_id": ObjectId(todo_id)})
    return convert_id(todo)


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str):
    result = await db["todos"].delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}
