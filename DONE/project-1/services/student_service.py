from models.student import Student, StudentUpdate

_students: list[Student] = []

def get_all() -> list[Student]:
    return _students

def get_by_name(name: str) -> Student | None:
    return next((s for s in _students if s.name == name), None)

def create(student: Student) -> Student:
    _students.append(student)
    return student

def update(name: str, data: StudentUpdate) -> Student | None:
    for i, s in enumerate(_students):
        if s.name == name:
            updated = s.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _students[i] = Student(**updated)
            return _students[i]
    return None

def delete(name: str) -> bool:
    for i, s in enumerate(_students):
        if s.name == name:
            _students.pop(i)
            return True
    return False
