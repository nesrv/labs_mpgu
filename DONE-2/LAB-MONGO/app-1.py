from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn

app = FastAPI()

# Подключение к MongoDB
client = MongoClient("mongodb://student:password@localhost:27017/")
db = client.testdb

@app.get("/")
def root():
    return {"message": "MongoDB FastAPI Server"}

@app.get("/ping")
def ping_mongodb():
    try:
        client.admin.command('ping')
        return {"status": "success", "message": "MongoDB connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/collections")
def list_collections():
    collections = db.list_collection_names()
    return {"collections": collections}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
