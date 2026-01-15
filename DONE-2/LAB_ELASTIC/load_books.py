import json
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    use_ssl=False
)

# Загрузить данные из JSON
with open('books-dataset.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# Загрузить каждую книгу
for book in books:
    client.index(index='books', body=book)
    print(f"Загружена: {book['title']}")

print(f"Всего загружено: {len(books)} книг")