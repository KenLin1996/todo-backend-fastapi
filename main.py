from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI()

# CORS 設定：允許的前端網址
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 待辦事項的模型
class Todo(BaseModel):
    id: str
    text: str
    completed: bool


# 新的待辦事項模型
class TodoCreate(BaseModel):
    text: str
    completed: bool = False


# 編輯使用的模型：欄位為選填
class EditTodo(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None  # 表示欄位可以是 bool，也可以是 None。


todos: List[Todo] = []


@app.get("/todos", response_model=List[Todo])
def get_todos():
    return todos


@app.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    new_todo = Todo(id=str(uuid4()), **todo.dict())
    todos.append(new_todo)
    return new_todo


@app.patch("/todos/edit/{todo_id}", response_model=Todo)
def edit_todo(todo_id: str, todo_edit: EditTodo):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            updated_data = todo.dict()

            # 根據傳入的資料更新欄位
            if todo_edit.text is not None:
                updated_data["text"] = todo_edit.text
            if todo_edit.completed is not None:
                updated_data["completed"] = todo_edit.completed

             # 更新清單中的項目
            updated_todo = Todo(**updated_data)
            todos[index] = updated_todo
            return updated_todo
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(index)
            return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")
