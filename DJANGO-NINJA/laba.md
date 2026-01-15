# 📘 Методичка: Создание REST API на Django с использованием Django Ninja

**Цель**: Научиться разрабатывать RESTful API с помощью Django Ninja, понимать ключевые концепции и применять их на практике.

---

## 🧩 1. Введение

### Почему Django Ninja?
- **Похож на FastAPI**: типизация, автоматическая валидация, интерактивная документация (Swagger/OpenAPI).
- **Лёгкая интеграция с Django**: ORM, аутентификация, настройки.
- **Высокая производительность** благодаря Pydantic.
- **Чистый и современный синтаксис**.


## 🛠 2. Подготовка стенда

1. Установите Python ≥ 3.13+.
2. Создайте виртуальное окружение:

```bash
uv venv
source .venv/bin/activate
```

3. Установите зависимости:
```bash
uv pip install django django-ninja
uv pip install django django>=6.0.0
```
4. Создайте проект:
```bash
django-admin startproject myapi
cd myapi
python manage.py startapp api
 ```

5. Добавьте `api` в `INSTALLED_APPS` (`settings.py`).

---

## 🏗️ 3. Базовая структура API

### Создайте файл `api/api.py`:

```python
from ninja import NinjaAPI
from django.http import JsonResponse

api = NinjaAPI()

@api.get("/hello")
def hello(request, name: str = "World"):
    return {"message": f"Hello {name}!"}
```

### Подключите API в `myapi/urls.py`:

```python
from django.contrib import admin
from django.urls import path
from api.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),  # ← основной эндпоинт
]
```

Запустите сервер:
```bash
python manage.py runserver
```

Откройте:
- `http://127.0.0.1:8000/api/hello?name=John`
- Документация: `http://127.0.0.1:8000/api/docs`

---

## 📦 4. Работа с моделями Django

### Пример модели (`api/models.py`):

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published = models.DateField()
```

Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Создайте схемы Pydantic (`api/schemas.py`):

```python
from datetime import date
from ninja import Schema

class BookIn(Schema):
    title: str
    author: str
    published: date

class BookOut(Schema):
    id: int
    title: str
    author: str
    published: date
```

### Добавьте CRUD-операции в `api/api.py`:

```python
from .models import Book
from .schemas import BookIn, BookOut

@api.post("/books", response=BookOut)
def create_book(request, payload: BookIn):
    book = Book.objects.create(**payload.dict())
    return book

@api.get("/books", response=list[BookOut])
def list_books(request):
    return Book.objects.all()

@api.get("/books/{book_id}", response=BookOut)
def get_book(request, book_id: int):
    return Book.objects.get(id=book_id)

@api.put("/books/{book_id}", response=BookOut)
def update_book(request, book_id: int, payload: BookIn):
    book = Book.objects.get(id=book_id)
    for attr, value in payload.dict().items():
        setattr(book, attr, value)
    book.save()
    return book

@api.delete("/books/{book_id}")
def delete_book(request, book_id: int):
    Book.objects.filter(id=book_id).delete()
    return {"success": True}
```

---

## 🔐 5. Аутентификация и авторизация

Django Ninja поддерживает стандартные механизмы Django:

```python
from ninja.security import django_auth

@api.get("/protected", auth=django_auth)
def protected_view(request):
    return {"user": str(request.user)}
```

Также можно создавать кастомные токены или использовать JWT (через сторонние пакеты).

---

## 🧪 6. Тестирование

Напишите тест в `api/tests.py`:

```python
from django.test import TestCase, Client
from .models import Book

class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_book(self):
        response = self.client.post(
            "/api/books",
            {"title": "Test Book", "author": "Author", "published": "2023-01-01"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 1)
```

Запустите:
```bash
python manage.py test
```

---

## 📚 7. Практические задания (для закрепления)

1. **Задание 1**: Создайте API для управления задачами (Task) с полями: `title`, `completed` (bool), `created_at`.
2. **Задание 2**: Добавьте фильтрацию по `completed`.
3. **Задание 3**: Реализуйте базовую аутентификацию (только авторизованные пользователи могут создавать задачи).
4. **Задание 4**: Напишите тесты для всех эндпоинтов.
5. **Задание 5** (продвинутое): Добавьте пагинацию и обработку ошибок (например, 404 при несуществующем ID).

---

## 📖 Полезные ресурсы

- Официальная документация: https://django-ninja.dev/
- Pydantic docs: https://docs.pydantic.dev/
- Django Ninja + Auth примеры: https://django-ninja.dev/guides/authentication/

---

## 💡 Советы

- Используйте типизацию — это упрощает отладку и даёт автодокументацию.
- Разделяйте схемы (`In`/`Out`) — особенно когда входные и выходные данные отличаются.
- Не забывайте про обработку исключений: `api.exception_handler`.

---

Готово! Эта методичка подходит как для индивидуального обучения, так и для проведения 2–3 часового воркшопа или лабораторной работы.