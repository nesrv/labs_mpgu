"""
Резолверы для CRUD операций с сообщениями

Этот файл содержит резолверы для:
- Create: создание нового сообщения
- Read: получение сообщений (список и по ID)
- Update: обновление данных сообщения
- Delete: удаление сообщения
"""

import json
from database import AsyncSessionLocal
from sqlalchemy import text
from models_graphql import MessageType, CommentType

# ============================================================================
# Read (чтение данных)
# ============================================================================

async def get_all_messages() -> list[MessageType]:
   
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM messages ORDER BY created_at DESC")
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]


async def get_message_by_id(message_id: int) -> MessageType | None:
 
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM messages WHERE id = :id"),
            {"id": message_id}
        )
        row = result.mappings().first()
        return MessageType(**row) if row else None

# ============================================================================
# Create (создание данных)
# ============================================================================

async def create_message(
    author_id: int,
    content: str,
    title: str | None = None,
    metadata: dict | None = None,
    stats: dict | None = None
) -> MessageType:
    async with AsyncSessionLocal() as session:
        metadata_json = json.dumps(metadata) if metadata else '{}'
        stats_json = json.dumps(stats) if stats else '{}'
        
        result = await session.execute(
            text("""
                INSERT INTO messages (author_id, title, content, metadata, stats)
                VALUES (:author_id, :title, :content, CAST(:metadata AS jsonb), CAST(:stats AS jsonb))
                RETURNING *
            """),
            {
                "author_id": author_id,
                "title": title,
                "content": content,
                "metadata": metadata_json,
                "stats": stats_json
            }
        )
        await session.commit()
        
        row = result.mappings().first()
        new_message = MessageType(**row) if row else None
        
        from pubsub import pubsub
        await pubsub.publish("messages", {
            "id": new_message.id,
            "author_id": new_message.author_id,
            "title": new_message.title,
            "content": new_message.content,
            "metadata": new_message.metadata,
            "stats": new_message.stats,
            "created_at": new_message.created_at,
            "updated_at": new_message.updated_at,
        })
        
        return new_message

# ============================================================================
# Update (обновление данных)
# ============================================================================

async def update_message(
    message_id: int,
    title: str | None = None,
    content: str | None = None,
    metadata: dict | None = None,
    stats: dict | None = None
) -> MessageType | None:
    """
    Обновить данные сообщения
    
    Параметры:
    - message_id: int - ID сообщения для обновления
    - title: str | None - новый заголовок сообщения (опционально)
    - content: str | None - новый текст сообщения (опционально)
    - metadata: dict | None - новые дополнительные данные (опционально)
    - stats: dict | None - новая статистика (опционально)
    
    Возвращает:
    - MessageType если сообщение найдено и обновлено
    - None если сообщение с указанным ID не существует
    
    Примечание:
    - Обновляет только переданные поля
    - Если поле не передано, оно остается без изменений
    - Автоматически обновляет updated_at
    
    Пример GraphQL мутации (обновление title и content):
    ```graphql
    mutation {
      updateMessage(
        messageId: 1
        title: "Обновленный заголовок"
        content: "Обновленное содержание"
      ) {
        id
        title
        content
        updatedAt
      }
    }
    ```
    
    Пример GraphQL мутации (обновление stats):
    ```graphql
    mutation {
      updateMessage(
        messageId: 1
        stats: {
          views: 200
          likes: 30
          comments_count: 8
        }
      ) {
        id
        stats
        updatedAt
      }
    }
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "updateMessage": {
          "id": 1,
          "title": "Обновленный заголовок",
          "content": "Обновленное содержание",
          "updatedAt": "2026-01-20T13:00:00"
        }
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        # Формируем динамический SQL запрос в зависимости от переданных полей
        updates = []
        params = {"id": message_id}
        
        if title is not None:
            updates.append("title = :title")
            params["title"] = title
        
        if content is not None:
            updates.append("content = :content")
            params["content"] = content
        
        if metadata is not None:
            updates.append("metadata = CAST(:metadata AS jsonb)")
            params["metadata"] = json.dumps(metadata)
        
        if stats is not None:
            updates.append("stats = CAST(:stats AS jsonb)")
            params["stats"] = json.dumps(stats)
        
        if not updates:
            # Если ничего не передано для обновления, просто возвращаем сообщение
            return await get_message_by_id(message_id)
        
        # Добавляем обновление updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        # Выполняем обновление и возвращаем обновленную запись
        result = await session.execute(
            text(f"""
                UPDATE messages
                SET {', '.join(updates)}
                WHERE id = :id
                RETURNING *
            """),
            params
        )
        await session.commit()
        
        row = result.mappings().first()
        updated_message = MessageType(**row) if row else None
        
        if updated_message:
            from pubsub import pubsub
            
            message_data = {
                "id": updated_message.id,
                "author_id": updated_message.author_id,
                "title": updated_message.title,
                "content": updated_message.content,
                "metadata": updated_message.metadata,
                "stats": updated_message.stats,
                "created_at": updated_message.created_at,
                "updated_at": updated_message.updated_at,
            }
            
            await pubsub.publish("message_updates:all", message_data)
            await pubsub.publish(f"message_updates:{updated_message.id}", message_data)
        
        return updated_message

# ============================================================================
# Delete (удаление данных)
# ============================================================================

async def delete_message(message_id: int) -> bool:
    """
    Удалить сообщение по ID
    
    Параметры:
    - message_id: int - уникальный идентификатор сообщения для удаления
    
    Возвращает:
    - bool: True если сообщение было удалено, False если не найдено
    
    Примечание:
    - Использует CASCADE для автоматического удаления связанных данных
    - Удаляет все комментарии к сообщению (ON DELETE CASCADE)
    
    Пример GraphQL мутации:
    ```graphql
    mutation {
      deleteMessage(messageId: 1)
    }
    ```
    
    Пример ответа (сообщение удалено):
    ```json
    {
      "data": {
        "deleteMessage": true
      }
    }
    ```
    
    Пример ответа (сообщение не найдено):
    ```json
    {
      "data": {
        "deleteMessage": false
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM messages WHERE id = :id RETURNING id"),
            {"id": message_id}
        )
        await session.commit()
        
        # Проверяем, была ли удалена хотя бы одна запись
        return result.rowcount > 0


async def create_comment(
    message_id: int,
    author_id: int,
    content: str,
    parent_comment_id: int | None = None,
    metadata: dict | None = None,
    reactions: dict | None = None
) -> CommentType:
    async with AsyncSessionLocal() as session:
        metadata_json = json.dumps(metadata) if metadata else '{}'
        reactions_json = json.dumps(reactions) if reactions else '{}'
        
        result = await session.execute(
            text("""
                INSERT INTO comments (message_id, author_id, parent_comment_id, content, metadata, reactions)
                VALUES (:message_id, :author_id, :parent_comment_id, :content, CAST(:metadata AS jsonb), CAST(:reactions AS jsonb))
                RETURNING *
            """),
            {
                "message_id": message_id,
                "author_id": author_id,
                "parent_comment_id": parent_comment_id,
                "content": content,
                "metadata": metadata_json,
                "reactions": reactions_json
            }
        )
        await session.commit()
        
        row = result.mappings().first()
        new_comment = CommentType(**row) if row else None
        
        from pubsub import pubsub
        channel = f"comments:{new_comment.message_id}"
        await pubsub.publish(channel, {
            "id": new_comment.id,
            "message_id": new_comment.message_id,
            "author_id": new_comment.author_id,
            "parent_comment_id": new_comment.parent_comment_id,
            "content": new_comment.content,
            "metadata": new_comment.metadata,
            "reactions": new_comment.reactions,
            "created_at": new_comment.created_at,
            "updated_at": new_comment.updated_at,
        })
        
        return new_comment