# models/todo.py
from pydantic import BaseModel
from typing import Optional


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
