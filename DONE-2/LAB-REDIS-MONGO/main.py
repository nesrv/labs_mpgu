from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient
import uvicorn
import os

# PostgreSQL setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# MongoDB setup
MONGODB_URL = os.getenv("MONGODB_URL")
mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client.testdb
mongo_collection = mongo_db.counter


class Counter(Base):
    __tablename__ = "counter"
    id = Column(Integer, primary_key=True, default=1)
    value = Column(Integer, default=0)



app = FastAPI()

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.get("/")
def read_root():
    return {"message": "PostgreSQL + MongoDB Lab"}

@app.post("/postgresql_hit")
async def postgresql_hit(db: AsyncSession = Depends(get_db)):
    counter = await db.get(Counter, 1)
    if not counter:
        counter = Counter(id=1, value=0)
        db.add(counter)
    counter.value += 1
    await db.commit()
    return {"database": "postgresql", "count": counter.value}

@app.post("/mongodb_hit")
def mongodb_hit():
    result = mongo_collection.find_one({"_id": "counter"})
    if not result:
        mongo_collection.insert_one({"_id": "counter", "value": 1})
        return {"database": "mongodb", "count": 1}
    
    new_value = result["value"] + 1
    mongo_collection.update_one(
        {"_id": "counter"}, 
        {"$set": {"value": new_value}}
    )
    return {"database": "mongodb", "count": new_value}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)