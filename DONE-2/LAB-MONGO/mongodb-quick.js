// MongoDB Быстрая шпаргалка

// === ЗАПУСК MONGOSH ===
// Из командной строки:
// mongosh --username student --password password
// Или из Docker:
// docker-compose exec mongodb mongosh --username student --password password

// === ОСНОВНЫЕ КОМАНДЫ ===
show dbs;              // Показать все базы данных
show collections;      // Показать коллекции в текущей БД
db;                    // Показать текущую БД
help;                  // Справка
exit;                  // Выход

// === ПОДКЛЮЧЕНИЕ ===
use library;           // Выбрать/создать БД

// === CREATE (Создание) ===
db.authors.insertOne({name: "Толстой", birthYear: 1828});
db.authors.insertMany([
  {name: "Толстой", birthYear: 1828},
  {name: "Достоевский", birthYear: 1821}
]);

// === READ (Чтение) ===
db.authors.find();                              // Все документы
db.authors.findOne({name: "Толстой"});          // Один документ
db.books.find({pages: {$gt: 500}});             // Больше 500 страниц
db.books.find({genre: "роман"}).limit(5);       // Первые 5

// === UPDATE (Обновление) ===
db.authors.updateOne(
  {name: "Толстой"},                  // Фильтр
  {$set: {country: "Россия"}}         // Обновление
);
db.books.updateMany(
  {genre: "роман"},
  {$set: {category: "классика"}}
);

// === DELETE (Удаление) ===
db.authors.deleteOne({name: "Толстой"});
db.books.deleteMany({pages: {$lt: 100}});

// === ОПЕРАТОРЫ ЗАПРОСОВ ===
{price: {$gt: 1000}}    // Больше
{price: {$gte: 1000}}   // Больше или равно
{price: {$lt: 1000}}    // Меньше
{price: {$lte: 1000}}   // Меньше или равно
{price: {$ne: 1000}}    // Не равно

// Логические
{$and: [{pages: {$gt: 500}}, {genre: "роман"}]}
{$or: [{genre: "роман"}, {genre: "повесть"}]}

// Массивы
{tags: {$in: ["классика", "роман"]}}      // Есть в массиве
{tags: {$nin: ["фантастика"]}}            // Нет в массиве

// === АГРЕГАЦИЯ ===

// Группировка
db.books.aggregate([
  {
    $group: {
      _id: "$genre",              // Группировать по жанру
      count: {$sum: 1},           // Подсчет
      avgPages: {$avg: "$pages"}  // Среднее
    }
  }
]);

// Сортировка и лимит
db.books.aggregate([
  {$sort: {pages: -1}},  // -1 = убывание, 1 = возрастание
  {$limit: 5}
]);

// Проекция (выбор полей)
db.books.aggregate([
  {
    $project: {
      title: 1,                    // Включить
      authorName: "$author.name",  // Переименовать
      _id: 0                       // Исключить
    }
  }
]);

// Lookup (JOIN)
db.books.aggregate([
  {
    $lookup: {
      from: "authors",        // Из какой коллекции
      localField: "authorId", // Поле в books
      foreignField: "_id",    // Поле в authors
      as: "author"            // Имя нового поля
    }
  },
  {$unwind: "$author"}  // Развернуть массив в объект
]);

// === ПОЛЕЗНЫЕ КОМАНДЫ ===
db.books.countDocuments({genre: "роман"});  // Подсчет
db.books.distinct("genre");                 // Уникальные значения
show collections;                           // Список коллекций
db.books.drop();                            // Удалить коллекцию

// ========================================
// === MONGODB COMPASS (GUI) ===
// ========================================

// ПОДКЛЮЧЕНИЕ:
// Connection String: mongodb://student:password@localhost:27017/

// === CREATE (Создание) ===
// 1. Выбрать коллекцию (например, authors)
// 2. Нажать кнопку "INSERT DOCUMENT"
// 3. Ввести JSON:
//    {"name": "Толстой", "birthYear": 1828, "country": "Россия"}
// 4. Нажать "INSERT"

// === READ (Чтение) ===
// 1. Открыть коллекцию
// 2. В поле Filter ввести запрос:
//    {"genre": "роман"}                    // Найти по жанру
//    {"pages": {"$gt": 500}}               // Больше 500 страниц
//    {"publishedYear": {"$gte": 1900}}    // С 1900 года
// 3. Нажать "FIND"

// === UPDATE (Обновление) ===
// 1. Найти документ через Filter
// 2. Навести на документ → нажать иконку карандаша (Edit)
// 3. Изменить поля в JSON
// 4. Нажать "UPDATE"

// === DELETE (Удаление) ===
// 1. Найти документ
// 2. Навести на документ → нажать иконку корзины (Delete)
// 3. Подтвердить удаление

// === AGGREGATIONS (Агрегация) ===
// 1. Перейти на вкладку "Aggregations"
// 2. Добавить стадии pipeline:
//    Stage 1: {"$match": {"genre": "роман"}}
//    Stage 2: {"$sort": {"pages": -1}}
//    Stage 3: {"$limit": 5}
// 3. Нажать "RUN" для просмотра результата

// === INDEXES (Индексы) ===
// 1. Перейти на вкладку "Indexes"
// 2. Нажать "CREATE INDEX"
// 3. Указать поля: {"name": 1}  // 1 = возрастание, -1 = убывание
// 4. Дать имя индексу
// 5. Нажать "CREATE"

// === SCHEMA (Схема) ===
// 1. Перейти на вкладку "Schema"
// 2. Нажать "ANALYZE SCHEMA"
// 3. Просмотреть типы данных и распределение значений

// === EXPORT/IMPORT ===
// Export:
// 1. Collection → Export Collection
// 2. Выбрать формат (JSON/CSV)
// 3. Сохранить файл
//
// Import:
// 1. Collection → Import Data
// 2. Выбрать файл
// 3. Нажать "IMPORT"