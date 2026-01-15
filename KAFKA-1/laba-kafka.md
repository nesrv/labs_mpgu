# Лабораторная работа: Обработка заказов в e-commerce с Apache Kafka

## Цель
Реализовать микросервисную архитектуру для обработки заказов интернет-магазина с использованием Apache Kafka 4.1 в качестве message broker.

## Задачи
1. Создать топики: `orders`, `payments`, `notifications`
2. Producer отправляет заказы в `orders`
3. Payment Service читает из `orders`, обрабатывает и пишет в `payments`
4. Notification Service читает из `payments` и отправляет уведомления
5. Реализовать обработку ошибок и retry логику

## Требования
- Python 3.13+
- Apache Kafka 4.1 (KRaft mode)
- kafka-python-ng библиотека (форк для Python 3.13+)
- Docker и Docker Compose

---

## Шаг 1: Установка и запуск Kafka 4.1 (KRaft mode)

### Docker Compose

Используйте готовый `docker-compose.yml` из папки KAFKA-1:

```yaml
services:
  kafka:
    image: apache/kafka:4.1.1
    container_name: kafka
    ports:
      - "19092:19092"
      - "9093:9093"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,EXTERNAL://0.0.0.0:19092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,EXTERNAL://localhost:19092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_LOG_DIRS: /var/lib/kafka/data
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka-data:/var/lib/kafka/data

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    depends_on:
      - kafka

volumes:
  kafka-data:
```

Запустите:
```bash
docker-compose up -d
```

**Важно:** 
- Kafka 4.1 использует KRaft (без Zookeeper)
- Подключайтесь к `localhost:19092` с хоста
- Kafka UI доступен по адресу http://localhost:8080

---

## Шаг 2: Создание топиков

```bash
# Создайте топики (используйте localhost:19092 для подключения с хоста)
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic orders --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic payments --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic notifications --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Проверьте созданные топики
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Альтернатива:** Используйте Kafka UI по адресу http://localhost:8080

---

## Шаг 3: Установка зависимостей

```bash
pip install kafka-python-ng fastapi uvicorn
```

**Важно:** Используйте `kafka-python-ng` вместо `kafka-python` для совместимости с Python 3.13+

---

## Шаг 4: Order Producer

Создайте `order_producer.py`:

```python
from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_order():
    return {
        'order_id': f'ORD-{random.randint(1000, 9999)}',
        'user_id': f'USER-{random.randint(1, 100)}',
        'amount': round(random.uniform(10.0, 500.0), 2),
        'items': random.randint(1, 5),
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    print('Order Producer started...')
    try:
        for i in range(10):
            order = generate_order()
            producer.send('orders', value=order)
            print(f'Sent order: {order}')
            time.sleep(2)
    except KeyboardInterrupt:
        print('\nStopping producer...')
    finally:
        producer.close()
```

---

## Шаг 5: Payment Service

Создайте `payment_service.py`:

```python
from kafka import KafkaConsumer, KafkaProducer
import json
import random
import time

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers='localhost:19092',
    group_id='payment-service',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_payment(order):
    time.sleep(1)  # Имитация обработки
    success = random.random() > 0.2  # 80% успешных платежей
    
    payment = {
        'order_id': order['order_id'],
        'user_id': order['user_id'],
        'amount': order['amount'],
        'status': 'SUCCESS' if success else 'FAILED',
        'payment_id': f'PAY-{random.randint(1000, 9999)}'
    }
    return payment

if __name__ == '__main__':
    print('Payment Service started...')
    try:
        for message in consumer:
            order = message.value
            print(f'Processing order: {order["order_id"]}')
            
            payment = process_payment(order)
            producer.send('payments', value=payment)
            print(f'Payment {payment["status"]}: {payment["payment_id"]}')
            
    except KeyboardInterrupt:
        print('\nStopping service...')
    finally:
        consumer.close()
        producer.close()
```

---

## Шаг 6: Notification Service

Создайте `notification_service.py`:

```python
from kafka import KafkaConsumer, KafkaProducer
import json

consumer = KafkaConsumer(
    'payments',
    bootstrap_servers='localhost:19092',
    group_id='notification-service',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_notification(payment):
    if payment['status'] == 'SUCCESS':
        message = f"Платеж {payment['payment_id']} успешно обработан. Сумма: {payment['amount']}"
    else:
        message = f"Платеж для заказа {payment['order_id']} отклонен"
    
    notification = {
        'user_id': payment['user_id'],
        'message': message,
        'type': 'EMAIL'
    }
    return notification

if __name__ == '__main__':
    print('Notification Service started...')
    try:
        for message in consumer:
            payment = message.value
            print(f'Received payment: {payment["payment_id"]} - {payment["status"]}')
            
            notification = send_notification(payment)
            producer.send('notifications', value=notification)
            print(f'Sent notification to {notification["user_id"]}: {notification["message"]}')
            
    except KeyboardInterrupt:
        print('\nStopping service...')
    finally:
        consumer.close()
        producer.close()
```

---

## Шаг 7: Запуск системы

1. Откройте 3 терминала
2. Запустите сервисы в следующем порядке:

```bash
# Терминал 1: Payment Service
python payment_service.py

# Терминал 2: Notification Service
python notification_service.py

# Терминал 3: Order Producer
python order_producer.py
```

---

## Шаг 8: Мониторинг

### Kafka UI (рекомендуется)

Откройте http://localhost:8080 для визуального мониторинга:
- Просмотр топиков и сообщений
- Мониторинг consumer groups
- Статистика и метрики

### Просмотр сообщений через CLI

```bash
# Orders
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic orders --from-beginning --bootstrap-server localhost:9092

# Payments
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic payments --from-beginning --bootstrap-server localhost:9092

# Notifications
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic notifications --from-beginning --bootstrap-server localhost:9092
```

### Проверка consumer groups

```bash
docker exec -it kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
docker exec -it kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group payment-service
```

---

## Задание для самостоятельной работы

1. **Retry логика**: Добавьте повторную обработку неудачных платежей
2. **Dead Letter Queue**: Создайте топик `failed-payments` для проблемных заказов
3. **Метрики**: Добавьте подсчет успешных/неудачных платежей
4. **Логирование**: Сохраняйте логи в файл
5. **Конфигурация**: Вынесите настройки в config файл

---

## Контрольные вопросы

1. Что произойдет, если Payment Service упадет во время обработки?
2. Как гарантировать, что сообщение обработано ровно один раз?
3. Зачем нужны партиции в топиках?
4. Что такое consumer group и как он работает?
5. Как масштабировать систему при увеличении нагрузки?
6. В чем преимущества KRaft mode перед Zookeeper?

---

## Результат

Вы создали микросервисную архитектуру с:
- Асинхронной обработкой заказов
- Разделением ответственности между сервисами
- Отказоустойчивостью через Kafka
- Возможностью горизонтального масштабирования
- Современным KRaft режимом без Zookeeper

---

## Шаг 9: Интеграция с FastAPI

### Установка зависимостей

```bash
pip install kafka-python-ng fastapi uvicorn
```

**Примечание:** `kafka-python-ng` - это активно поддерживаемый форк для Python 3.13+

---

### API Service

Создайте `api_service.py`:

```python
from fastapi import FastAPI, HTTPException
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
from pydantic import BaseModel
from typing import List
import threading

app = FastAPI(title="E-commerce Order API")

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class Order(BaseModel):
    user_id: str
    amount: float
    items: int

class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str

# Хранилище для последних уведомлений
notifications_cache = []

def consume_notifications():
    consumer = KafkaConsumer(
        'notifications',
        bootstrap_servers='localhost:19092',
        group_id='api-service',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest'
    )
    for message in consumer:
        notifications_cache.append(message.value)
        if len(notifications_cache) > 100:
            notifications_cache.pop(0)

# Запуск consumer в фоновом потоке
threading.Thread(target=consume_notifications, daemon=True).start()

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: Order):
    try:
        import random
        from datetime import datetime
        
        order_data = {
            'order_id': f'ORD-{random.randint(1000, 9999)}',
            'user_id': order.user_id,
            'amount': order.amount,
            'items': order.items,
            'timestamp': datetime.now().isoformat()
        }
        
        producer.send('orders', value=order_data)
        producer.flush()
        
        return OrderResponse(
            order_id=order_data['order_id'],
            status="PENDING",
            message="Order created successfully"
        )
    except KafkaError as e:
        raise HTTPException(status_code=500, detail=f"Kafka error: {str(e)}")

@app.get("/notifications")
async def get_notifications(limit: int = 10):
    return notifications_cache[-limit:]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "kafka": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Запуск API

```bash
python api_service.py
```

API будет доступен по адресу: http://localhost:8000

---

### Тестирование API

#### Swagger UI
Откройте http://localhost:8000/docs для интерактивной документации

#### cURL примеры

```bash
# Создать заказ
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER-123",
    "amount": 299.99,
    "items": 3
  }'

# Получить уведомления
curl "http://localhost:8000/notifications?limit=5"

# Health check
curl "http://localhost:8000/health"
```

#### Python requests

```python
import requests

# Создать заказ
response = requests.post(
    "http://localhost:8000/orders",
    json={
        "user_id": "USER-456",
        "amount": 150.50,
        "items": 2
    }
)
print(response.json())

# Получить уведомления
notifications = requests.get("http://localhost:8000/notifications").json()
print(notifications)
```

---

### Полный запуск системы с API

```bash
# Терминал 1: Payment Service
python payment_service.py

# Терминал 2: Notification Service
python notification_service.py

# Терминал 3: API Service
python api_service.py

# Терминал 4: Тестирование
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER-1", "amount": 100, "items": 1}'
```

---

### Дополнительное задание (изучение Kafka)

1. **Kafka Streams для статистики**: Создайте endpoint, который использует KTable для агрегации статистики по платежам (успешные/неудачные) в реальном времени

2. **Transactional Producer**: Модифицируйте API для использования транзакционного producer с exactly-once семантикой

3. **Consumer Lag Monitoring**: Добавьте endpoint `/metrics/lag`, который показывает отставание consumer groups от последних сообщений в топиках

4. **Custom Partitioner**: Реализуйте кастомный partitioner для распределения заказов по партициям на основе user_id (все заказы одного пользователя в одну партицию)

5. **Dead Letter Queue**: Создайте топик `failed-orders` и механизм отправки туда заказов, которые не удалось обработать после 3 попыток

6. **Kafka Headers**: Добавьте в сообщения Kafka headers с метаданными (correlation_id, timestamp, source) и используйте их для трейсинга запросов

7. **Compacted Topic**: Создайте топик `order-status` с log compaction для хранения последнего статуса каждого заказа (key: order_id, value: status)

8. **Multiple Consumer Groups**: Создайте второй consumer group для аналитики, который читает те же топики параллельно с основными сервисами
