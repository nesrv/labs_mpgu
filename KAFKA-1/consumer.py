from kafka import KafkaConsumer
from kafka.errors import KafkaError
import sys

try:
    consumer = KafkaConsumer(
        'hello-kafka',
        bootstrap_servers='localhost:19092',
        group_id='hello-group',
        auto_offset_reset='earliest',
        value_deserializer=lambda v: v.decode('utf-8')
    )
    
    print("Consumer подключён к Kafka")
    print("Ожидание сообщений...")
    print("(Нажмите Ctrl+C для остановки)")
    print("\n💡 Подсказка: Запустите producer.py в другом терминале, чтобы отправить сообщения\n")
    
    message_count = 0
    for msg in consumer:
        message_count += 1
        print(f"✓ Получено [{message_count}]: {msg.value}")
        print(f"  Partition: {msg.partition}, Offset: {msg.offset}, Timestamp: {msg.timestamp}")
    
except KeyboardInterrupt:
    print("\n\nConsumer остановлен пользователем")
    consumer.close()
except KafkaError as e:
    print(f"Ошибка Kafka: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Ошибка подключения к Kafka: {e}")
    print("Убедитесь, что Kafka запущен: docker-compose ps")
    sys.exit(1)
finally:
    if 'consumer' in locals():
        consumer.close()