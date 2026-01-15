
├── main.py                    # Точка входа
├── api/                       # API Уровень (Представление)
│   ├── __init__.py
│   └── students.py            # REST эндпоинты студентов
│   
│  
├── services/                  # Уровень бизнес-логики
│   └── student_service.py     # Бизнес-логика студентов
│   
│  
├── repositories/              # Уровень доступа к данным
│   └── student_repository.py  # Операции с данными студентов
│  
│  
├── models/                    # Доменные модели
│   └── student.py             # Модель Student
│   
├── schemas/                   # Схемы API
│   └── student.py             # DTO студентов
│   
│  
├── database/                  # Конфигурация БД
│   |── __init__.py            # Настройка БД (заглушка)
│   └── database.py
└── fixtures.json    


почему в терминале vs code ctrl + c не останавливает фастапи сервер