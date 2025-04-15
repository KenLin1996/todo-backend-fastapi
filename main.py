from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import todos

app = FastAPI()


app.include_router(todos.router)

origins = [
    "http://localhost:3000",  # 本機開發用
    "https://nuxt3-todo.vercel.app/"  # Vercel 正式網址
]

# CORS 設定：允許的前端網址
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# class Todo(BaseModel):
#     id: str
#     text: str
#     completed: bool


# class TodoCreate(BaseModel):
#     text: str
#     completed: bool = False


# class EditTodo(BaseModel):
#     text: Optional[str] = None
#     completed: Optional[bool] = None


# todos: List[Todo] = []


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


# @app.get("/todos", response_model=List[Todo])
# def get_todos():
#     return todos


# @app.post("/todos", response_model=Todo)
# def create_todo(todo: TodoCreate):
#     new_todo = Todo(id=str(uuid4()), **todo.dict())
#     todos.append(new_todo)
#     return new_todo


# @app.patch("/todos/edit/{todo_id}", response_model=Todo)
# def edit_todo(todo_id: str, todo_edit: EditTodo):
#     for index, todo in enumerate(todos):
#         if todo.id == todo_id:
#             updated_data = todo.dict()

#             if todo_edit.text is not None:
#                 updated_data["text"] = todo_edit.text
#             if todo_edit.completed is not None:
#                 updated_data["completed"] = todo_edit.completed

#             updated_todo = Todo(**updated_data)
#             todos[index] = updated_todo
#             return updated_todo
#     raise HTTPException(status_code=404, detail="Todo not found")


# @app.delete("/todos/{todo_id}")
# def delete_todo(todo_id: str):
#     for index, todo in enumerate(todos):
#         if todo.id == todo_id:
#             todos.pop(index)
#             return {"message": "Todo deleted"}
#     raise HTTPException(status_code=404, detail="Todo not found")
