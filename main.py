from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4

app = FastAPI()


# 待辦事項的模型
class Todo(BaseModel):
    id: str
    text: str
    completed: bool


# 新的待辦事項模型
class TodoCreate(BaseModel):
    text: str
    completed: bool = False


todos: List[Todo] = []


@app.get("/todos", response_model=List[Todo])
def get_todos():
    return todos


@app.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    new_todo = Todo(id=str(uuid4()), **todo.dict())
    todos.append(new_todo)
    return new_todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, updated_todo: TodoCreate):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[index] = Todo(id=todo_id, **updated_todo.dict())
            return todos[index]
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(index)
            return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")
