from fastapi import FastAPI
import psycopg2
import httpx
import asyncio

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 5435,
    "database": "testdb",
    "user": "user",
    "password": "password",
    "client_encoding": "utf8"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

@app.on_event("startup")
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS counter (id INT PRIMARY KEY, value INT)")
    cur.execute("INSERT INTO counter (id, value) VALUES (1, 0) ON CONFLICT (id) DO NOTHING")
    conn.commit()
    cur.close()
    conn.close()

@app.post("/increment")
def increment():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True}

@app.post("/reset")
def reset():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE counter SET value = 0 WHERE id = 1")
    conn.commit()
    cur.close()
    conn.close()
    return {"reset": True}

@app.get("/result")
def result(expected: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM counter WHERE id = 1")
    actual = cur.fetchone()[0]
    cur.close()
    conn.close()
    lost = expected - actual
    return {"expected": expected, "actual": actual, "lost": lost}

@app.post("/test")
async def test(total_requests: int, concurrent: int):
    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:8000/reset")
        
        tasks = []
        for _ in range(total_requests):
            tasks.append(client.post("http://localhost:8000/increment"))
        
        semaphore = asyncio.Semaphore(concurrent)
        
        async def limited_request(task):
            async with semaphore:
                return await task
        
        await asyncio.gather(*[limited_request(task) for task in tasks])
        
        response = await client.get(f"http://localhost:8000/result?expected={total_requests}")
        return response.json()
