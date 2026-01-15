from fastapi import APIRouter, HTTPException
from models.student import Student, StudentUpdate
from services import student_service as service

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/")
def get_all() -> list[Student]:
    return service.get_all()

@router.get("/{name}")
def get_one(name: str) -> Student:
    student = service.get_by_name(name)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/")
def create(student: Student) -> Student:
    return service.create(student)

@router.patch("/{name}")
def update(name: str, data: StudentUpdate) -> Student:
    student = service.update(name, data)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.delete("/{name}")
def delete(name: str):
    if not service.delete(name):
        raise HTTPException(404, "Student not found")
    return {"message": "Deleted"}