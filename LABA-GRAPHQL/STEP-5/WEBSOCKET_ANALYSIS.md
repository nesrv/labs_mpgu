# Анализ и варианты реализации WebSocket для информационного канала мессенджера

## Текущее состояние проекта

**Архитектура:**
- FastAPI + Strawberry GraphQL
- PostgreSQL (async SQLAlchemy)
- Модели: User, Message, Comment
- Реализованы: Query, Mutation
- **Не реализовано:** Subscriptions (real-time обновления)

**Цель STEP-5:** Добавить real-time функциональность через WebSocket для:
- Мгновенное получение новых сообщений канала
- Обновление комментариев в реальном времени
- Уведомления о действиях пользователей
- Статусы онлайн/оффлайн

---

## Вариант 1: GraphQL Subscriptions (Strawberry) — Рекомендуется

### Описание
Использование нативных GraphQL Subscriptions через Strawberry. Это стандартный подход для GraphQL API, который интегрируется с существующей схемой.

### Преимущества
✅ **Единая точка входа** — все через `/graphql` (HTTP для Query/Mutation, WebSocket для Subscriptions)  
✅ **Типобезопасность** — та же схема, те же типы  
✅ **Консистентность** — один язык запросов (GraphQL)  
✅ **Автодокументация** — Subscriptions видны в GraphQL Playground  
✅ **Стандартный подход** — соответствует GraphQL спецификации  

### Недостатки
⚠️ **Сложность настройки** — требует дополнительной инфраструктуры (pub/sub)  
⚠️ **Ограничения Strawberry** — меньше примеров, чем у Apollo Server  

### Технический стек
- `strawberry-graphql[fastapi]` — уже установлен
- `python-multipart` — для WebSocket поддержки
- **Pub/Sub система:** Redis, PostgreSQL LISTEN/NOTIFY, или in-memory (для разработки)

### Архитектура

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ WebSocket (GraphQL Subscription)
       │
┌──────▼─────────────────────────────────┐
│         FastAPI + Strawberry            │
│  ┌──────────────────────────────────┐   │
│  │  GraphQL Router                  │   │
│  │  - Query (HTTP)                  │   │
│  │  - Mutation (HTTP)               │   │
│  │  - Subscription (WebSocket)       │   │
│  └──────────────────────────────────┘   │
│              │                           │
│              ▼                           │
│  ┌──────────────────────────────────┐   │
│  │  Pub/Sub Manager                 │   │
│  │  (Redis / PostgreSQL / In-Memory)│   │
│  └──────────────────────────────────┘   │
└──────┬───────────────────────────────────┘
       │
       │ Publish events
       │
┌──────▼──────┐
│  Resolvers  │
│  (Mutations)│
└─────────────┘
```

### Пример реализации

**1. Создание Pub/Sub менеджера:**

```python
# pubsub.py
from typing import AsyncIterator, Dict, List
import asyncio
from collections import defaultdict

class PubSubManager:
    """Простой in-memory pub/sub для разработки"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
        """Подписаться на канал"""
        queue = asyncio.Queue()
        async with self._lock:
            self.subscribers[channel].append(queue)
        
        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            async with self._lock:
                if queue in self.subscribers[channel]:
                    self.subscribers[channel].remove(queue)
    
    async def publish(self, channel: str, message: dict):
        """Опубликовать сообщение в канал"""
        async with self._lock:
            for queue in self.subscribers[channel]:
                await queue.put(message)

# Глобальный экземпляр
pubsub = PubSubManager()
```

**2. Добавление Subscriptions в схему:**

```python
# schema.py (дополнение)
import strawberry
from typing import AsyncIterator
from pubsub import pubsub

@strawberry.type
class Subscription:
    """GraphQL Subscriptions для real-time обновлений"""
    
    @strawberry.subscription
    async def message_added(self) -> AsyncIterator[MessageType]:
        """Подписка на новые сообщения канала"""
        async for message_data in pubsub.subscribe("messages"):
            # Преобразуем данные в MessageType
            yield MessageType(**message_data)
    
    @strawberry.subscription
    async def comment_added(
        self, 
        message_id: int
    ) -> AsyncIterator[CommentType]:
        """Подписка на комментарии к конкретному сообщению"""
        channel = f"comments:{message_id}"
        async for comment_data in pubsub.subscribe(channel):
            yield CommentType(**comment_data)
    
    @strawberry.subscription
    async def message_updated(
        self,
        message_id: int | None = None
    ) -> AsyncIterator[MessageType]:
        """Подписка на обновления сообщений"""
        channel = f"message_updates:{message_id}" if message_id else "message_updates:all"
        async for message_data in pubsub.subscribe(channel):
            yield MessageType(**message_data)

# Обновление схемы
schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation,
    subscription=Subscription  # Добавляем подписки
)
```

**3. Публикация событий в мутациях:**

```python
# message_resolvers.py (дополнение)
from pubsub import pubsub

async def create_message(...) -> MessageType:
    # ... существующая логика создания ...
    
    # Публикуем событие для подписчиков
    await pubsub.publish("messages", {
        "id": new_message.id,
        "author_id": new_message.author_id,
        "title": new_message.title,
        "content": new_message.content,
        "created_at": new_message.created_at.isoformat(),
        # ... остальные поля
    })
    
    return new_message
```

**4. Настройка FastAPI для WebSocket:**

```python
# main.py (дополнение)
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware

# GraphQL роутер с поддержкой subscriptions
graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql",
    # WebSocket настройки уже включены в strawberry-graphql[fastapi]
)

app = FastAPI(...)
app.include_router(graphql_app, prefix="/graphql")
```

### Пример использования (клиент)

```graphql
# Подписка на новые сообщения
subscription {
  messageAdded {
    id
    title
    content
    author {
      username
    }
    createdAt
  }
}

# Подписка на комментарии к сообщению
subscription {
  commentAdded(messageId: 1) {
    id
    content
    author {
      username
    }
    createdAt
  }
}
```

### Когда использовать
- ✅ Когда нужна консистентность с существующим GraphQL API
- ✅ Когда клиенты уже используют GraphQL
- ✅ Для учебного проекта (демонстрация полного GraphQL стека)

---

## Вариант 2: Нативные WebSocket через FastAPI

### Описание
Прямая реализация WebSocket через FastAPI, без использования GraphQL Subscriptions. Отдельный endpoint для WebSocket соединений.

### Преимущества
✅ **Простота** — не требует pub/sub инфраструктуры  
✅ **Гибкость** — полный контроль над протоколом  
✅ **Производительность** — меньше накладных расходов  
✅ **Легкая отладка** — простой протокол (JSON)  

### Недостатки
⚠️ **Дублирование логики** — отдельная реализация от GraphQL  
⚠️ **Нет автодокументации** — нужно документировать вручную  
⚠️ **Разные протоколы** — GraphQL для HTTP, JSON для WebSocket  

### Архитектура

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ├─── HTTP ────► /graphql (Query/Mutation)
       │
       └─── WebSocket ────► /ws (Real-time events)
              │
┌─────────────▼─────────────────────────┐
│         FastAPI                        │
│  ┌──────────────────────────────────┐  │
│  │  /graphql (GraphQL Router)      │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  /ws (WebSocket Handler)         │  │
│  │  - Connection Manager            │  │
│  │  - Event Broadcasting             │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### Пример реализации

**1. WebSocket Connection Manager:**

```python
# websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio

class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        # Активные соединения по каналам
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Подключить клиента к каналу"""
        await websocket.accept()
        async with self._lock:
            self.active_connections[channel].add(websocket)
    
    async def disconnect(self, websocket: WebSocket, channel: str):
        """Отключить клиента от канала"""
        async with self._lock:
            self.active_connections[channel].discard(websocket)
    
    async def broadcast(self, channel: str, message: dict):
        """Отправить сообщение всем подписчикам канала"""
        async with self._lock:
            disconnected = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Удаляем отключенные соединения
            self.active_connections[channel] -= disconnected

manager = ConnectionManager()
```

**2. WebSocket endpoint в FastAPI:**

```python
# main.py (дополнение)
from fastapi import WebSocket, WebSocketDisconnect
from websocket_manager import manager
import json

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, channel: str = "messages"):
    """
    WebSocket endpoint для real-time обновлений
    
    Параметры:
    - channel: канал подписки (messages, comments:{id}, etc.)
    """
    await manager.connect(websocket, channel)
    
    try:
        while True:
            # Можно принимать команды от клиента
            data = await websocket.receive_text()
            command = json.loads(data)
            
            # Обработка команд (например, переключение канала)
            if command.get("type") == "subscribe":
                await manager.disconnect(websocket, channel)
                channel = command.get("channel", "messages")
                await manager.connect(websocket, channel)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

# Публикация событий в мутациях
async def create_message(...) -> MessageType:
    # ... создание сообщения ...
    
    # Отправка через WebSocket
    await manager.broadcast("messages", {
        "type": "message_added",
        "data": {
            "id": new_message.id,
            "title": new_message.title,
            "content": new_message.content,
            # ...
        }
    })
    
    return new_message
```

**3. Клиентский пример (JavaScript):**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?channel=messages');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'message_added') {
        console.log('Новое сообщение:', message.data);
        // Обновить UI
    }
};

// Подписка на другой канал
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'comments:1'
}));
```

### Когда использовать
- ✅ Когда нужна максимальная простота
- ✅ Когда WebSocket используется только для уведомлений
- ✅ Когда не требуется интеграция с GraphQL схемой

---

## Вариант 3: Гибридный подход (GraphQL + WebSocket)

### Описание
GraphQL для Query/Mutation через HTTP, отдельный WebSocket endpoint для real-time событий. События могут быть в формате GraphQL или JSON.

### Преимущества
✅ **Разделение ответственности** — HTTP для запросов, WebSocket для событий  
✅ **Гибкость протокола** — можно использовать простой JSON для событий  
✅ **Оптимизация** — легкие события через WebSocket, тяжелые запросы через HTTP  

### Недостатки
⚠️ **Два протокола** — нужно поддерживать оба  
⚠️ **Сложность** — больше кода для поддержки  

### Архитектура

```
Client
  │
  ├── HTTP ────► /graphql (Query/Mutation)
  │
  └── WebSocket ────► /ws/events (Real-time)
         │
         │ Простой JSON протокол:
         │ {
         │   "event": "message_added",
         │   "data": {...}
         │ }
```

### Когда использовать
- ✅ Когда нужна максимальная производительность
- ✅ Когда события простые (не требуют GraphQL гибкости)
- ✅ Когда есть разные типы клиентов (мобильные, веб)

---

## Вариант 4: Redis Pub/Sub (Production-ready)

### Описание
Использование Redis для pub/sub вместо in-memory решения. Подходит для production и масштабирования.

### Преимущества
✅ **Масштабируемость** — работает с несколькими инстансами сервера  
✅ **Надежность** — Redis гарантирует доставку  
✅ **Производительность** — оптимизирован для pub/sub  

### Недостатки
⚠️ **Дополнительная зависимость** — нужен Redis  
⚠️ **Сложность** — больше инфраструктуры  

### Технический стек
- `redis` или `aioredis` — для async работы
- Redis server (можно через Docker)

### Пример реализации

```python
# pubsub_redis.py
import aioredis
from typing import AsyncIterator
import json

class RedisPubSub:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: aioredis.Redis = None
        self.pubsub: aioredis.client.PubSub = None
    
    async def connect(self):
        """Подключиться к Redis"""
        self.redis = await aioredis.from_url(self.redis_url)
        self.pubsub = self.redis.pubsub()
    
    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
        """Подписаться на канал"""
        await self.pubsub.subscribe(channel)
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                yield data
    
    async def publish(self, channel: str, message: dict):
        """Опубликовать сообщение"""
        await self.redis.publish(channel, json.dumps(message))
```

---

## Рекомендации для STEP-5

### Для учебного проекта (рекомендуется):

**Вариант 1: GraphQL Subscriptions с in-memory pub/sub**

**Почему:**
- ✅ Демонстрирует полный GraphQL стек (Query, Mutation, Subscription)
- ✅ Минимальные зависимости (не нужен Redis)
- ✅ Легко понять и объяснить
- ✅ Интегрируется с существующей схемой

**План реализации:**

1. **Создать pub/sub менеджер** (`pubsub.py`)
   - In-memory реализация для начала
   - Можно позже заменить на Redis

2. **Добавить Subscription класс** в `schema.py`
   - `messageAdded` — новые сообщения
   - `commentAdded` — новые комментарии
   - `messageUpdated` — обновления сообщений

3. **Обновить мутации** для публикации событий
   - `create_message` → публикует в "messages"
   - `create_comment` → публикует в "comments:{message_id}"

4. **Обновить main.py**
   - Убедиться, что WebSocket включен в GraphQLRouter

5. **Тестирование**
   - GraphQL Playground поддерживает subscriptions
   - Или использовать Apollo Studio

### Для production (если нужно):

**Вариант 4: GraphQL Subscriptions с Redis**

- Заменить in-memory pub/sub на Redis
- Добавить Docker Compose для Redis
- Настроить мониторинг и логирование

---

## Сравнительная таблица

| Критерий | Вариант 1 (GraphQL Subscriptions) | Вариант 2 (FastAPI WebSocket) | Вариант 3 (Гибридный) | Вариант 4 (Redis) |
|----------|-----------------------------------|-------------------------------|----------------------|-------------------|
| **Сложность** | Средняя | Низкая | Высокая | Средняя |
| **Интеграция с GraphQL** | ✅ Полная | ❌ Нет | ⚠️ Частичная | ✅ Полная |
| **Зависимости** | Минимум | Минимум | Минимум | Redis |
| **Масштабируемость** | ⚠️ In-memory | ❌ Нет | ⚠️ Зависит | ✅ Да |
| **Типобезопасность** | ✅ Да | ❌ Нет | ⚠️ Частичная | ✅ Да |
| **Автодокументация** | ✅ Да | ❌ Нет | ⚠️ Частичная | ✅ Да |
| **Для учебного проекта** | ✅✅✅ | ✅✅ | ✅ | ✅✅ |

---

## Следующие шаги

1. **Выбрать вариант** (рекомендуется Вариант 1)
2. **Создать структуру файлов** в STEP-5
3. **Реализовать pub/sub менеджер**
4. **Добавить Subscriptions в схему**
5. **Обновить мутации для публикации событий**
6. **Протестировать через GraphQL Playground**
7. **Создать пример клиента** (JavaScript/TypeScript)

---

## Полезные ссылки

- [Strawberry Subscriptions Documentation](https://strawberry.rocks/docs/guides/subscriptions)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [GraphQL Subscriptions Spec](https://graphql.org/learn/queries/#subscriptions)
- [Redis Pub/Sub](https://redis.io/docs/manual/pubsub/)

---

*Документ создан для STEP-5: Добавление WebSocket функциональности*

