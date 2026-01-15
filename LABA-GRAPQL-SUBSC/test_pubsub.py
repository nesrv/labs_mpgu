import asyncio
from pubsub import pubsub

async def test_pubsub():
    """Тест pub/sub механизма"""
    
    async def subscriber():
        """Подписчик - получает события"""
        print("Подписчик: жду события...")
        async for event in pubsub.subscribe("test_channel"):
            print(f"Подписчик: получил {event}")
            break  # Получили одно событие и выходим
    
    async def publisher():
        """Издатель - отправляет события"""
        await asyncio.sleep(1)  # Ждем, пока подписчик подключится
        print("Издатель: отправляю событие...")
        await pubsub.publish("test_channel", {"message": "Hello, Pub/Sub!"})
    
    # Запускаем подписчика и издателя параллельно
    await asyncio.gather(subscriber(), publisher())

if __name__ == "__main__":
    asyncio.run(test_pubsub())