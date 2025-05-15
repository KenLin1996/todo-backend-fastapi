# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import todos, user, test

app = FastAPI()


origins = [
    "http://localhost:3000",  # 本機開發用
    "https://nuxt3-todo.vercel.app",  # Vercel 正式網址
    "https://nuxt3-todo-8owhhv9d5-lins-projects-1cf87d8a.vercel.app"
]

# CORS 設定：允許的前端網址
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)
app.include_router(user.router)
app.include_router(test.router)


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}
