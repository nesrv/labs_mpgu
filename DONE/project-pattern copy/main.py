from fastapi import FastAPI
from api import students, courses

app = FastAPI()
app.include_router(students.router)
app.include_router(courses.router)