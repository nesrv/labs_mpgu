from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn

app = FastAPI()

# Подключение к MongoDB
client = MongoClient("mongodb://student:password@localhost:27017/")
db = client.library

# Задание 1: Топ-5 самых длинных книг
@app.get("/books/longest")
def get_longest_books():
    """Найти 5 самых длинных книг с информацией об авторах"""
    pipeline = [
        {"$sort": {"pages": -1}},  # Сортировка по убыванию страниц
        {"$limit": 5},              # Взять первые 5
        {
            "$lookup": {
                "from": "authors",
                "localField": "authorId",
                "foreignField": "_id",
                "as": "author"
            }
        },
        {"$unwind": "$author"},
        {
            "$project": {
                "title": 1,
                "pages": 1,
                "authorName": "$author.name",
                "publishedYear": 1
            }
        }
    ]
    return list(db.books.aggregate(pipeline))

# Задание 2: Средний рейтинг каждой книги
@app.get("/books/ratings")
def get_books_ratings():
    """Получить среднюю оценку для каждой книги"""
    pipeline = [
        {
            "$group": {
                "_id": "$bookId",
                "avgRating": {"$avg": "$rating"},
                "reviewCount": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "books",
                "localField": "_id",
                "foreignField": "_id",
                "as": "book"
            }
        },
        {"$unwind": "$book"},
        {
            "$project": {
                "title": "$book.title",
                "avgRating": {"$round": ["$avgRating", 2]},
                "reviewCount": 1
            }
        },
        {"$sort": {"avgRating": -1}}
    ]
    return list(db.reviews.aggregate(pipeline))

# Задание 3: Статистика по авторам
@app.get("/authors/stats")
def get_authors_stats():
    """Количество книг и общее число страниц для каждого автора"""
    pipeline = [
        {
            "$group": {
                "_id": "$authorId",
                "bookCount": {"$sum": 1},
                "totalPages": {"$sum": "$pages"},
                "avgPages": {"$avg": "$pages"}
            }
        },
        {
            "$lookup": {
                "from": "authors",
                "localField": "_id",
                "foreignField": "_id",
                "as": "author"
            }
        },
        {"$unwind": "$author"},
        {
            "$project": {
                "authorName": "$author.name",
                "bookCount": 1,
                "totalPages": 1,
                "avgPages": {"$round": ["$avgPages", 0]}
            }
        },
        {"$sort": {"bookCount": -1}}
    ]
    return list(db.books.aggregate(pipeline))

# Задание 4: Книги по жанрам
@app.get("/books/by-genre")
def get_books_by_genre():
    """Группировка книг по жанрам с подсчетом"""
    pipeline = [
        {
            "$group": {
                "_id": "$genre",
                "count": {"$sum": 1},
                "books": {"$push": "$title"},
                "avgPages": {"$avg": "$pages"}
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(db.books.aggregate(pipeline))

# Задание 5: Поиск книг по диапазону лет
@app.get("/books/by-years/{start_year}/{end_year}")
def get_books_by_years(start_year: int, end_year: int):
    """Найти книги, опубликованные в заданном диапазоне лет"""
    pipeline = [
        {
            "$match": {
                "publishedYear": {"$gte": start_year, "$lte": end_year}
            }
        },
        {
            "$lookup": {
                "from": "authors",
                "localField": "authorId",
                "foreignField": "_id",
                "as": "author"
            }
        },
        {"$unwind": "$author"},
        {
            "$project": {
                "title": 1,
                "authorName": "$author.name",
                "publishedYear": 1,
                "genre": 1
            }
        },
        {"$sort": {"publishedYear": 1}}
    ]
    return list(db.books.aggregate(pipeline))

# Бонус: Самый активный рецензент
@app.get("/reviewers/top")
def get_top_reviewers():
    """Найти самых активных рецензентов"""
    pipeline = [
        {
            "$group": {
                "_id": "$reviewerName",
                "reviewCount": {"$sum": 1},
                "avgRating": {"$avg": "$rating"}
            }
        },
        {"$sort": {"reviewCount": -1}},
        {"$limit": 5}
    ]
    return list(db.reviews.aggregate(pipeline))

# Бонус: Книги без отзывов
@app.get("/books/no-reviews")
def get_books_without_reviews():
    """Найти книги, у которых нет отзывов"""
    pipeline = [
        {
            "$lookup": {
                "from": "reviews",
                "localField": "_id",
                "foreignField": "bookId",
                "as": "reviews"
            }
        },
        {
            "$match": {
                "reviews": {"$size": 0}
            }
        },
        {
            "$lookup": {
                "from": "authors",
                "localField": "authorId",
                "foreignField": "_id",
                "as": "author"
            }
        },
        {"$unwind": "$author"},
        {
            "$project": {
                "title": 1,
                "authorName": "$author.name",
                "publishedYear": 1
            }
        }
    ]
    return list(db.books.aggregate(pipeline))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)