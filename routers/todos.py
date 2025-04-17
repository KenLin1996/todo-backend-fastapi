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
async def create_todo(todo: TodoCreate):
    first_todo = await db["todos"].find_one(sort=[("order", 1)])
    # 如果沒有任何待辦事項，則設置新的 todo 的 order 為 1
    if first_todo is None:
        new_order = 1
    else:
        # 如果已有待辦事項，則將所有 todo 的 order 增加 1，再將新的 todo 排在最前面
        await db["todos"].update_many(
            {},  # 更新所有資料
            {"$inc": {"order": 1}}  # 每一筆的 order 都加 1
        )
        new_order = 1  # 新的 todo order 設為最小，排最前面

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
