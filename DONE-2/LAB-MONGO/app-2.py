from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Подключение к MongoDB
client = MongoClient("mongodb://student:password@localhost:27017/")
db = client.library

# Модели
class Author(BaseModel):
    name: str
    birthYear: int
    country: str

class Book(BaseModel):
    title: str
    authorId: str
    pages: int
    publishedYear: int
    genre: str

class Review(BaseModel):
    bookId: str
    rating: int
    comment: str
    reviewerName: str

# CRUD для авторов
@app.get("/authors")
def get_authors():
    # Получить всех авторов из коллекции
    authors = list(db.authors.find())
    # Преобразовать ObjectId в строку для JSON
    for author in authors:
        author["_id"] = str(author["_id"])
    return authors

@app.post("/authors")
def create_author(author: Author):
    # Вставить нового автора в коллекцию
    result = db.authors.insert_one(author.dict())
    return {"id": str(result.inserted_id)}

@app.get("/authors/{author_id}")
def get_author(author_id: str):
    # Найти автора по ID
    try:
        author = db.authors.find_one({"_id": ObjectId(author_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    author["_id"] = str(author["_id"])
    return author

# CRUD для книг
@app.get("/books")
def get_books():
    # Получить все книги
    books = list(db.books.find())
    # Преобразовать ObjectId в строку
    for book in books:
        book["_id"] = str(book["_id"])
        book["authorId"] = str(book["authorId"])
    return books

@app.post("/books")
def create_book(book: Book):
    # Преобразовать authorId из строки в ObjectId
    book_dict = book.dict()
    book_dict["authorId"] = ObjectId(book_dict["authorId"])
    # Вставить книгу в коллекцию
    result = db.books.insert_one(book_dict)
    return {"id": str(result.inserted_id)}

@app.get("/books/{book_id}")
def get_book(book_id: str):
    # Найти книгу по ID
    try:
        book = db.books.find_one({"_id": ObjectId(book_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book["_id"] = str(book["_id"])
    book["authorId"] = str(book["authorId"])
    return book

# CRUD для отзывов
@app.get("/reviews")
def get_reviews():
    reviews = list(db.reviews.find())
    for review in reviews:
        review["_id"] = str(review["_id"])
        review["bookId"] = str(review["bookId"])
    return reviews

@app.post("/reviews")
def create_review(review: Review):
    review_dict = review.dict()
    review_dict["bookId"] = ObjectId(review_dict["bookId"])
    result = db.reviews.insert_one(review_dict)
    return {"id": str(result.inserted_id)}

@app.get("/reviews/book/{book_id}")
def get_book_reviews(book_id: str):
    reviews = list(db.reviews.find({"bookId": ObjectId(book_id)}))
    for review in reviews:
        review["_id"] = str(review["_id"])
        review["bookId"] = str(review["bookId"])
    return reviews

# Агрегация: книги с авторами
@app.get("/books-with-authors")
def get_books_with_authors():
    # Pipeline для агрегации
    pipeline = [
        {
            # $lookup - соединяет коллекции books и authors
            "$lookup": {
                "from": "authors",           # Из какой коллекции
                "localField": "authorId",    # Поле в books
                "foreignField": "_id",       # Поле в authors
                "as": "author"               # Имя нового поля
            }
        },
        # $unwind - разворачивает массив author в объект
        {"$unwind": "$author"}
    ]
    # Выполнить агрегацию
    books = list(db.books.aggregate(pipeline))
    # Преобразовать ObjectId в строку
    for book in books:
        book["_id"] = str(book["_id"])
        book["authorId"] = str(book["authorId"])
        book["author"]["_id"] = str(book["author"]["_id"])
    return books

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)