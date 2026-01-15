from typing import AsyncIterator, Dict, List
import asyncio
from collections import defaultdict


class PubSubManager:
    
    def __init__(self):
        self.subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
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
        async with self._lock:
            disconnected = []
            for queue in self.subscribers[channel]:
                try:
                    await queue.put(message)
                except Exception:
                    disconnected.append(queue)
            
            for queue in disconnected:
                if queue in self.subscribers[channel]:
                    self.subscribers[channel].remove(queue)


# Глобальный экземпляр менеджера
# Импортируйте его в других файлах: from pubsub import pubsub
pubsub = PubSubManager()