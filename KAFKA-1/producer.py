from kafka import KafkaProducer
from kafka.errors import KafkaError
import time
import sys

print("Подключение к Kafka...")
print("   Bootstrap servers: localhost:19092")
print("   Topic: hello-kafka\n")

try:
    producer = KafkaProducer(
        bootstrap_servers='localhost:19092',
        value_serializer=lambda v: v.encode('utf-8')
    )
    
    print("[OK] Producer подключен к Kafka")
    print("[>>] Отправка сообщений...\n")
    
    success_count = 0
    error_count = 0
    
    for i in range(1, 6):
        message = f"Hello Kafka {i}"
        
        try:
            future = producer.send('hello-kafka', message)
            
            # Ждём подтверждения отправки
            record_metadata = future.get(timeout=10)
            success_count += 1
            print(f"[OK] [{success_count}] Отправлено: {message}")
            print(f"     Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
            
        except KafkaError as e:
            error_count += 1
            print(f"[ERROR] [{error_count}] Ошибка при отправке '{message}': {e}")
        except Exception as e:
            error_count += 1
            print(f"[ERROR] [{error_count}] Неожиданная ошибка при отправке '{message}': {e}")
        
        time.sleep(0.5)  # Уменьшил задержку для быстрой отправки
    
    # Принудительно отправляем все оставшиеся сообщения
    print("\n[>>] Flush (отправка всех оставшихся сообщений)...")
    producer.flush(timeout=10)
    
    producer.close()
    
    print(f"\n[ИТОГИ]:")
    print(f"   [OK] Успешно отправлено: {success_count}")
    if error_count > 0:
        print(f"   [ERROR] Ошибок: {error_count}")
    print(f"   Всего попыток: {success_count + error_count}")
    
    if success_count > 0:
        print("\n[OK] Сообщения успешно отправлены в Kafka!")
        print("[INFO] Проверьте сообщения:")
        print("   - В Kafka UI: http://localhost:8080")
        print("   - Или запустите consumer: python consumer.py")
    else:
        print("\n[WARNING] Не удалось отправить ни одного сообщения!")
        print("   Проверьте:")
        print("   1. Kafka запущен: docker-compose ps")
        print("   2. Порт 9092 доступен")
        print("   3. Топик hello-kafka существует")
        sys.exit(1)
    
except Exception as e:
    print(f"\n[ERROR] Критическая ошибка подключения к Kafka:")
    print(f"   {type(e).__name__}: {e}")
    print("\n[DIAG] Диагностика:")
    print("   1. Проверьте, что Kafka запущен:")
    print("      docker-compose ps")
    print("   2. Проверьте логи Kafka:")
    print("      docker logs kafka --tail 20")
    print("   3. Проверьте, что порт 9092 не занят:")
    print("      netstat -an | findstr 9092")
    sys.exit(1)