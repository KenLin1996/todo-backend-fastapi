# routers/todos.py
from fastapi import APIRouter, HTTPException, Depends, Body
from db.mongodb import db
from bson import ObjectId
from typing import List
from auths.auth import get_current_user
from models.user import UserInDB
from models.todo import TodoCreate, EditTodo, TodoOrderUpdate, TodoOrderRequest


router = APIRouter()


def convert_id(todo):
    todo["id"] = str(todo["_id"])
    del todo["_id"]
    return todo


@router.get("/todos")
async def get_todos(current_user: UserInDB = Depends(get_current_user)):
    todos = await db["todos"].find({"user_id":current_user.id}).to_list(10)
    return [convert_id(todo) for todo in todos]


@router.post("/todos")
async def create_todo(todo: TodoCreate, current_user: UserInDB  = Depends(get_current_user)):
    first_todo = await db["todos"].find_one({"user_id": current_user.id},sort=[("order", 1)])
    if first_todo is None:
        new_order = 1
    else:
        await db["todos"].update_many(
            {"user_id": current_user.id},
            {"$inc": {"order": 1}}
        )
        new_order = 1

    todo_data = {
        "text": todo.text,
        "completed": todo.completed,
        "order": new_order,
        "user_id": current_user.id
    }

    result = await db["todos"].insert_one(todo_data)
    new_todo = await db["todos"].find_one({"_id": result.inserted_id})
    return [convert_id(new_todo)]


@router.patch("/todos/edit/{todo_id}")
async def edit_todo(
    todo_id: str,
    todo_edit: EditTodo,
    current_user: UserInDB = Depends(get_current_user)
):
    update_data = {k: v for k, v in todo_edit.dict().items() if v is not None}

    result = await db["todos"].update_one(
        {
            "_id": ObjectId(todo_id),
            "user_id": current_user.id
        },
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    updated_todo = await db["todos"].find_one({
        "_id": ObjectId(todo_id),
        "user_id": current_user.id
    })
    return convert_id(updated_todo)


# @router.put("/todos/reorder")
# async def reorder_todos(order_updates: List[TodoOrderUpdate]):
#     for update in order_updates:
#         result = await db["todos"].update_one(
#             {"_id": ObjectId(update.id)},
#             {"$set":{"order": update.order}}
#         )
#         if result.matched_count == 0:
#             raise HTTPException(status_code=404, datail=f"Todo with ID {update.id} not found")
#     return {"message":"Reordering successful"}

@router.put("/todos/reorder")
async def reorder_todos(
    order_update: TodoOrderRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    new_order = order_update.new_order

    user_todos = await db["todos"].find({"user_id": current_user.id}).to_list(1000)
    user_todo_ids = {str(todo["_id"]) for todo in user_todos}

    if set(new_order) - user_todo_ids:
        raise HTTPException(status_code=403, detail="Trying to modify others' todos")

    for index, todo_id in enumerate(new_order):
        await db["todos"].update_one(
            {"_id": ObjectId(todo_id), "user_id": current_user.id},
            {"$set": {"order": index + 1}}
        )

    updated_todos = await db["todos"].find({"user_id": current_user.id}).sort("order").to_list(1000)
    return [convert_id(todo) for todo in updated_todos]


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str , current_user: UserInDB = Depends(get_current_user)):
    result = await db["todos"].delete_one({"_id": ObjectId(todo_id), "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}
