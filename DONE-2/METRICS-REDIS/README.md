# Тестирование производительности БД

## Запуск

1. Поднять базы данных:
```bash
docker-compose up -d
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Запустить сервер:
```bash
uvicorn main:app --reload
```

4. Открыть Swagger UI: http://localhost:8000/docs

## Тестирование с помощью ab

### PostgreSQL
```bash
ab -n 1000 -c 50 -p post.json -T application/json http://localhost:8000/test/postgres
```

### MongoDB
```bash
ab -n 1000 -c 50 -p post.json -T application/json http://localhost:8000/test/mongodb
```

### Redis
```bash
ab -n 1000 -c 50 -p post.json -T application/json http://localhost:8000/test/redis
```

Создайте файл `post.json`:
```json
{"total_requests": 1000, "concurrent": 50}
```

## Использование через Swagger

1. Перейдите на http://localhost:8000/docs
2. Выберите эндпоинт (postgres/mongodb/redis)
3. Укажите параметры:
   - `total_requests`: общее количество запросов (например, 1000)
   - `concurrent`: количество конкурентных потоков (например, 50)
4. Нажмите Execute

Ответ покажет количество потерянных данных.
