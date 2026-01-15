# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = None

_students: list[Student] = []

@app.get("/students")
def get_all() -> list[Student]:
    return _students

@app.get("/students/{name}")
def get_one(name: str) -> Student:
    for student in _students:
        if student.name == name:
            return student
    raise HTTPException(404, "Student not found")

@app.post("/students")
def create(student: Student) -> Student:
    _students.append(student)
    return student

@app.patch("/students/{name}")
def update(name: str, update: StudentUpdate) -> Student:
    for i, student in enumerate(_students):
        if student.name == name:
            data = student.model_dump()
            data.update(update.model_dump(exclude_unset=True))
            _students[i] = Student(**data)
            return _students[i]
    raise HTTPException(404, "Student not found")

@app.delete("/students/{name}")
def delete(name: str):
    for i, student in enumerate(_students):
        if student.name == name:
            _students.pop(i)
            return {"message": "Student deleted"}
    raise HTTPException(404, "Student not found")
