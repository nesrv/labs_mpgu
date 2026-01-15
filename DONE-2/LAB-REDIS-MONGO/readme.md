ТЗ
поднять 3 контейнера
postgesql 17
mongodb


создать fastapi приложение (в одном файле)
в нем модель

class Counter(Base):
    __tablename__ = "counter"
    id = Column(Integer, primary_key=True, default=1)
    value = Column(Integer, default=0)

DATABASE_URL = "postgresql+asyncpg://student:password@db:5432/student_db"
и ссылку для подключения mongodb

Counter для postgesql и аналогичную для mongodb



app = FastAPI()


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all

@app.post("/postgresql_hit")
async def hit(db: AsyncSession = Depends(get_db)):
    counter = await db.get(Counter, 1)
    if not counter:
        counter = Counter(id=1, value=0)
        db.add(counter)
    counter.value += 1
    await db.commit()
    return {"count": counter.value}

@app.post("/mongodb_hit")
...

