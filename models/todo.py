# models/todo.py
from pydantic import BaseModel
from typing import Optional


# 待辦事項的模型（回傳用，會包含 id 和 order）
class Todo(BaseModel):
    id: str
    text: str
    completed: bool
    order: int


# 新的待辦事項模型（建立用，前端可不傳 order，就從最大值 + 1）
class TodoCreate(BaseModel):
    text: str
    completed: bool = False
    order: Optional[int] = None


# 編輯使用的模型（欄位為選填）
class EditTodo(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None  # 表示欄位可以是 bool，也可以是 None。
    order: Optional[int] = None
