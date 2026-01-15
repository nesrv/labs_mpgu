#!/usr/bin/env python3
"""Тестовый скрипт для проверки подключения к Kafka"""

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import sys

def test_producer():
    """Тест отправки сообщения"""
    print("=" * 50)
    print("ТЕСТ PRODUCER")
    print("=" * 50)
    
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:19092',
            value_serializer=lambda v: v.encode('utf-8'),
            request_timeout_ms=30000,
            max_block_ms=30000
        )
        
        print("✅ Producer создан")
        
        # Отправляем одно тестовое сообщение
        print("📤 Отправка тестового сообщения...")
        future = producer.send('hello-kafka', 'TEST MESSAGE')
        
        # Ждём подтверждения
        record_metadata = future.get(timeout=10)
        print(f"✅ Сообщение отправлено успешно!")
        print(f"   Topic: {record_metadata.topic}")
        print(f"   Partition: {record_metadata.partition}")
        print(f"   Offset: {record_metadata.offset}")
        
        producer.flush()
        producer.close()
        return True
        
    except KafkaError as e:
        print(f"❌ Ошибка Kafka: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        return False

def test_consumer():
    """Тест чтения сообщения"""
    print("\n" + "=" * 50)
    print("ТЕСТ CONSUMER")
    print("=" * 50)
    
    try:
        consumer = KafkaConsumer(
            'hello-kafka',
            bootstrap_servers='localhost:19092',
            group_id='test-group',
            auto_offset_reset='earliest',
            value_deserializer=lambda v: v.decode('utf-8'),
            consumer_timeout_ms=5000
        )
        
        print("✅ Consumer создан")
        print("📥 Ожидание новых сообщений (5 сек)...")
        
        message_count = 0
        for msg in consumer:
            message_count += 1
            print(f"✅ Получено сообщение:")
            print(f"   Value: {msg.value}")
            print(f"   Partition: {msg.partition}")
            print(f"   Offset: {msg.offset}")
            break  # Читаем только одно сообщение
        
        consumer.close()
        
        if message_count == 0:
            print("⚠️ Сообщений не получено (таймаут)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тестирование подключения к Kafka\n")
    
    # Тест producer
    producer_ok = test_producer()
    
    if producer_ok:
        # Небольшая задержка
        import time
        time.sleep(1)
        
        # Тест consumer
        consumer_ok = test_consumer()
        
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 50)
        print(f"Producer: {'✅ OK' if producer_ok else '❌ FAIL'}")
        print(f"Consumer: {'✅ OK' if consumer_ok else '❌ FAIL'}")
        
        if producer_ok and consumer_ok:
            print("\n✅ Все тесты пройдены!")
            sys.exit(0)
        else:
            print("\n❌ Некоторые тесты не пройдены")
            sys.exit(1)
    else:
        print("\n❌ Producer не работает - проверьте подключение к Kafka")
        sys.exit(1)
