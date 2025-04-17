# routers/todos.py
from fastapi import APIRouter, HTTPException
from db.mongodb import db
from bson import ObjectId
from typing import List
from models.todo import TodoCreate, EditTodo, TodoOrderUpdate


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
    last_todo = await db["todos"].find_one(sort=[("order", -1)])
    max_todo = last_todo["order"] if last_todo and "order" in last_todo else 0

    new_order = todo.order if todo.order is not None else max_todo + 1

    todo_data = {
        "text": todo.text,
        "completed": todo.completed,
        "order": new_order
    }

    # result = await db["todos"].insert_one(todo.dict())
    result = await db["todos"].insert_one(todo_data)
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


@router.put("/todos/reorder")
async def reorder_todos(order_updates: List[TodoOrderUpdate]):
    for update in order_updates:
        result = await db["todos"].update_one(
            {"_id": ObjectId(update.id)},
            {"$set":{"order": update.order}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, datail=f"Todo with ID {update.id} not found")
    return {"message":"Reordering successful"}


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str):
    result = await db["todos"].delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}
