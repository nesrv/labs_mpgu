from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = None

