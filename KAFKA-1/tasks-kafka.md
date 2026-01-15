# Практические задания по работе с Kafka

## Задание 1: Первое знакомство с Kafka

**Цель:** Запустить Kafka и проверить его работоспособность

**Задачи:**
1. Запустите контейнеры: `docker-compose up -d`
2. Проверьте статус контейнеров: `docker ps`
3. Откройте Kafka UI: http://localhost:8080
4. Проверьте логи Kafka: `docker logs kafka`

**Ожидаемый результат:** Kafka и Kafka UI запущены и доступны

---

## Задание 2: Работа с топиками через CLI

**Цель:** Научиться создавать и управлять топиками

**Задачи:**
```bash
# 1. Создайте топик test-topic с 3 партициями
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

# 2. Выведите список всех топиков
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --list --bootstrap-server localhost:9092

# 3. Получите детальную информацию о топике
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --describe --topic test-topic \
  --bootstrap-server localhost:9092

# 4. Удалите топик
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --delete --topic test-topic \
  --bootstrap-server localhost:9092
```

**Ожидаемый результат:** Топик создан, описан и удален

---

## Задание 3: Console Producer и Consumer

**Цель:** Отправить и получить сообщения через консоль

**Задачи:**
```bash
# Терминал 1: Запустите consumer
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic messages \
  --bootstrap-server localhost:9092 \
  --from-beginning

# Терминал 2: Запустите producer и отправьте сообщения
docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh \
  --topic messages \
  --bootstrap-server localhost:9092

# Введите несколько сообщений:
> Hello Kafka!
> This is message 2
> Message 3
```

**Ожидаемый результат:** Сообщения из producer появляются в consumer

---

## Задание 4: Producer с ключами

**Цель:** Понять партиционирование по ключам

**Задачи:**
```bash
# Producer с ключами (key:value)
docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh \
  --topic keyed-messages \
  --bootstrap-server localhost:9092 \
  --property "parse.key=true" \
  --property "key.separator=:"

# Отправьте сообщения:
> user1:Login event
> user2:Purchase event
> user1:Logout event
> user3:View event

# Consumer с выводом ключей
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic keyed-messages \
  --bootstrap-server localhost:9092 \
  --from-beginning \
  --property "print.key=true" \
  --property "key.separator=:"
```

**Ожидаемый результат:** Сообщения с одинаковым ключом попадают в одну партицию

---

## Задание 5: Consumer Groups

**Цель:** Изучить работу consumer groups

**Задачи:**
```bash
# Создайте топик с 3 партициями
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic group-test \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

# Терминал 1: Consumer в группе A
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic group-test \
  --bootstrap-server localhost:9092 \
  --group group-a

# Терминал 2: Еще один consumer в группе A
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic group-test \
  --bootstrap-server localhost:9092 \
  --group group-a

# Терминал 3: Producer отправляет сообщения
docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh \
  --topic group-test \
  --bootstrap-server localhost:9092

# Терминал 4: Проверьте consumer groups
docker exec -it kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group group-a
```

**Ожидаемый результат:** Сообщения распределяются между consumers в группе

---

## Задание 6: Python Producer

**Цель:** Написать простой producer на Python

**Задачи:**

Создайте файл `simple_producer.py`:
```python
from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for i in range(10):
    message = {'id': i, 'text': f'Message {i}'}
    producer.send('python-topic', value=message)
    print(f'Sent: {message}')
    time.sleep(1)

producer.close()
```

Запустите:
```bash
pip install kafka-python-ng
python simple_producer.py
```

Проверьте в Kafka UI или через consumer

**Ожидаемый результат:** 10 сообщений отправлено в топик

---

## Задание 7: Python Consumer

**Цель:** Написать простой consumer на Python

**Задачи:**

Создайте файл `simple_consumer.py`:
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'python-topic',
    bootstrap_servers='localhost:19092',
    group_id='python-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

print('Waiting for messages...')
for message in consumer:
    print(f'Partition: {message.partition}')
    print(f'Offset: {message.offset}')
    print(f'Value: {message.value}')
    print('---')
```

Запустите:
```bash
python simple_consumer.py
```

**Ожидаемый результат:** Consumer читает сообщения из топика

---

## Задание 8: Мониторинг через Kafka UI

**Цель:** Изучить возможности Kafka UI

**Задачи:**
1. Откройте http://localhost:8080
2. Перейдите в раздел "Topics"
3. Выберите любой топик и просмотрите:
   - Количество партиций
   - Количество сообщений
   - Размер данных
4. Перейдите в "Messages" и просмотрите содержимое
5. Перейдите в "Consumer Groups" и проверьте lag
6. Создайте новый топик через UI

**Ожидаемый результат:** Понимание интерфейса Kafka UI

---

## Задание 9: Измерение производительности

**Цель:** Протестировать пропускную способность Kafka

**Задачи:**
```bash
# Producer performance test (100k сообщений)
docker exec -it kafka /opt/kafka/bin/kafka-producer-perf-test.sh \
  --topic perf-test \
  --num-records 100000 \
  --record-size 1000 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092

# Consumer performance test
docker exec -it kafka /opt/kafka/bin/kafka-consumer-perf-test.sh \
  --topic perf-test \
  --bootstrap-server localhost:9092 \
  --messages 100000 \
  --threads 1
```

**Ожидаемый результат:** Метрики производительности (MB/sec, records/sec)

---

## Задание 10: Работа с JSON сообщениями

**Цель:** Отправить и обработать структурированные данные

**Задачи:**

Создайте файл `json_example.py`:
```python
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime
import threading
import time

# Producer
def produce():
    producer = KafkaProducer(
        bootstrap_servers='localhost:19092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    users = ['Alice', 'Bob', 'Charlie']
    actions = ['login', 'purchase', 'logout', 'view']
    
    for i in range(20):
        event = {
            'event_id': i,
            'user': users[i % len(users)],
            'action': actions[i % len(actions)],
            'timestamp': datetime.now().isoformat(),
            'amount': (i * 10) if actions[i % len(actions)] == 'purchase' else None
        }
        producer.send('user-events', key=event['user'].encode(), value=event)
        print(f'Produced: {event}')
        time.sleep(0.5)
    
    producer.close()

# Consumer
def consume():
    consumer = KafkaConsumer(
        'user-events',
        bootstrap_servers='localhost:19092',
        group_id='event-processor',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    
    for message in consumer:
        event = message.value
        if event['action'] == 'purchase':
            print(f"💰 {event['user']} purchased for ${event['amount']}")
        else:
            print(f"📊 {event['user']} - {event['action']}")

# Запуск
threading.Thread(target=consume, daemon=True).start()
time.sleep(2)
produce()
```

Запустите:
```bash
python json_example.py
```

**Ожидаемый результат:** События отправляются и обрабатываются с фильтрацией

---

## Бонусное задание: Очистка

**Удалите все созданные ресурсы:**
```bash
# Остановите контейнеры
docker-compose down

# Удалите volumes (данные Kafka)
docker-compose down -v

# Запустите заново
docker-compose up -d
```

---

## Полезные команды

```bash
# Проверить версию Kafka
docker exec -it kafka /opt/kafka/bin/kafka-broker-api-versions.sh \
  --bootstrap-server localhost:9092

# Посмотреть конфигурацию топика
docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
  --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name test-topic \
  --describe

# Изменить retention топика
docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
  --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name test-topic \
  --alter --add-config retention.ms=3600000
```
