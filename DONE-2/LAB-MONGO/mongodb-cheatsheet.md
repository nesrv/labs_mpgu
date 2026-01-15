# MongoDB Шпаргалка для app-2.py

## 🔌 Подключение к MongoDB

```python
from pymongo import MongoClient
from bson import ObjectId

# Подключение
client = MongoClient("mongodb://student:password@localhost:27017/")
db = client.library  # Выбор базы данных
```

## 📝 CRUD Операции

### CREATE (Создание)

```python
# Вставить один документ
result = db.authors.insert_one({"name": "Толстой", "birthYear": 1828})
inserted_id = result.inserted_id  # Получить ID нового документа

# Вставить несколько документов
result = db.authors.insert_many([
    {"name": "Толстой", "birthYear": 1828},
    {"name": "Достоевский", "birthYear": 1821}
])
```

### READ (Чтение)

```python
# Найти все документы
authors = list(db.authors.find())

# Найти один документ
author = db.authors.find_one({"name": "Толстой"})

# Найти по ID
author = db.authors.find_one({"_id": ObjectId("674e1234...")})

# Найти с условием
books = list(db.books.find({"pages": {"$gt": 500}}))  # Больше 500 страниц
```

### UPDATE (Обновление)

```python
# Обновить один документ
db.authors.update_one(
    {"name": "Толстой"},           # Фильтр
    {"$set": {"country": "Россия"}} # Обновление
)

# Обновить несколько документов
db.books.update_many(
    {"genre": "роман"},
    {"$set": {"category": "классика"}}
)
```

### DELETE (Удаление)

```python
# Удалить один документ
db.authors.delete_one({"name": "Толстой"})

# Удалить несколько документов
db.books.delete_many({"pages": {"$lt": 100}})
```

## 🔑 Работа с ObjectId

```python
from bson import ObjectId

# Преобразовать строку в ObjectId
author_id = ObjectId("674e1234567890abcdef1234")

# Преобразовать ObjectId в строку
id_string = str(author_id)

# Проверка валидности
try:
    ObjectId(some_string)
except:
    print("Невалидный ObjectId")
```

## 🔗 Связи между коллекциями

### Хранение связи
```python
# В коллекции books храним authorId
{
    "title": "Война и мир",
    "authorId": ObjectId("674e1234..."),  # Ссылка на автора
    "pages": 1225
}
```

### Получение связанных данных (Lookup)
```python
pipeline = [
    {
        "$lookup": {
            "from": "authors",        # Из какой коллекции
            "localField": "authorId", # Поле в books
            "foreignField": "_id",    # Поле в authors
            "as": "author"            # Имя нового поля
        }
    },
    {"$unwind": "$author"}  # Развернуть массив в объект
]
books = list(db.books.aggregate(pipeline))
```

## 📊 Операторы запросов

### Сравнение
```python
{"price": {"$gt": 1000}}   # Больше
{"price": {"$gte": 1000}}  # Больше или равно
{"price": {"$lt": 1000}}   # Меньше
{"price": {"$lte": 1000}}  # Меньше или равно
{"price": {"$ne": 1000}}   # Не равно
```

### Логические
```python
{"$and": [{"pages": {"$gt": 500}}, {"genre": "роман"}]}
{"$or": [{"genre": "роман"}, {"genre": "повесть"}]}
```

### Массивы
```python
{"tags": {"$in": ["классика", "роман"]}}      # Есть в массиве
{"tags": {"$nin": ["фантастика"]}}            # Нет в массиве
```

## 🎯 Агрегация

### Группировка
```python
pipeline = [
    {
        "$group": {
            "_id": "$genre",              # Группировать по жанру
            "count": {"$sum": 1},         # Подсчет
            "avgPages": {"$avg": "$pages"} # Среднее
        }
    }
]
```

### Сортировка и лимит
```python
pipeline = [
    {"$sort": {"pages": -1}},  # -1 = по убыванию, 1 = по возрастанию
    {"$limit": 5}              # Взять первые 5
]
```

### Проекция (выбор полей)
```python
pipeline = [
    {
        "$project": {
            "title": 1,           # Включить поле
            "authorName": "$author.name",  # Переименовать
            "_id": 0              # Исключить поле
        }
    }
]
```

## 🛠️ Полезные функции для FastAPI

### Преобразование ObjectId в JSON
```python
def convert_objectid(doc):
    """Преобразовать ObjectId в строку для JSON"""
    doc["_id"] = str(doc["_id"])
    if "authorId" in doc:
        doc["authorId"] = str(doc["authorId"])
    return doc

# Использование
authors = list(db.authors.find())
authors = [convert_objectid(a) for a in authors]
```

### Обработка ошибок
```python
from fastapi import HTTPException

try:
    author = db.authors.find_one({"_id": ObjectId(author_id)})
except:
    raise HTTPException(status_code=400, detail="Invalid ObjectId")

if not author:
    raise HTTPException(status_code=404, detail="Not found")
```

## 📚 Примеры из app-2.py

### Получить все книги с авторами
```python
pipeline = [
    {
        "$lookup": {
            "from": "authors",
            "localField": "authorId",
            "foreignField": "_id",
            "as": "author"
        }
    },
    {"$unwind": "$author"}
]
books = list(db.books.aggregate(pipeline))
```

### Создать книгу со связью
```python
book_dict = {
    "title": "Война и мир",
    "authorId": ObjectId("674e1234..."),  # Преобразовать строку в ObjectId
    "pages": 1225
}
result = db.books.insert_one(book_dict)
```

### Получить отзывы по книге
```python
reviews = list(db.reviews.find({"bookId": ObjectId(book_id)}))
```

## 🔍 Отладка

```python
# Вывести запрос
print(list(db.books.find({"genre": "роман"})))

# Подсчет документов
count = db.books.count_documents({"genre": "роман"})

# Проверить существование
exists = db.books.find_one({"_id": ObjectId(book_id)}) is not None
```