
### Структура проекта

```
lab-postgres/
├── main.py              # FastAPI приложение
├── database.py          # Подключение к БД
├── models.py            # SQLAlchemy модели
├── schemas.py           # Pydantic схемы
├── init_db.sql          # SQL для инициализации
└── requirements.txt     # Зависимости
```


### database.py

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://user:password@localhost/lab_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### models.py

```python
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    grades: Mapped[list["Grade"]] = relationship(back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int] = mapped_column(default=3)
    
    grades: Mapped[list["Grade"]] = relationship(back_populates="course")

class Grade(Base):
    __tablename__ = "grades"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    grade: Mapped[float] = mapped_column(Float)
    
    student: Mapped["Student"] = relationship(back_populates="grades")
    course: Mapped["Course"] = relationship(back_populates="grades")
```

### schemas.py

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    email: str
    status: str = 'active'

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GradeResponse(BaseModel):
    student_id: int
    course_id: int
    grade: float
    
    model_config = ConfigDict(from_attributes=True)
```


```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

app = FastAPI()


metadata = MetaData()
active_students_table = Table('active_students_view', metadata, autoload_with=engine)


@app.post("/admin/execute-sql")
def execute_sql(sql_command: str, db: Session = Depends(get_db)):
    """Выполнение произвольных SQL команд (только для разработки!)"""
    try:
        result = db.execute(text(sql_command))
        db.commit()
        
        # Пытаемся получить результат, если это SELECT
        try:
            rows = result.fetchall()
            return {
                "status": "success",
                "rows_affected": len(rows),
                "data": [dict(row._mapping) for row in rows]
            }
        except:
            return {"status": "success", "message": "Command executed"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}



@app.get("/students/active/raw")
def get_active_students_raw(db: Session = Depends(get_db)):
    """Получение активных студентов через raw SQL"""
    result = db.execute(text("SELECT * FROM active_students_view"))
    students = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "count": len(students), "data": students}


# Отражаем view как таблицу
metadata = MetaData()
active_students_table = Table('active_students_view', metadata, autoload_with=engine)

@app.get("/students/active/sqlalchemy")
def get_active_students_sqlalchemy(db: Session = Depends(get_db)):
    """Получение активных студентов через SQLAlchemy"""
    stmt = select(active_students_table)
    result = db.execute(stmt)
    students = [dict(row._mapping) for row in result]
    return {"method": "sqlalchemy", "count": len(students), "data": students}

```