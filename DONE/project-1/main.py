# main.py
from fastapi import FastAPI
from routers import students

app = FastAPI()
app.include_router(students.router)