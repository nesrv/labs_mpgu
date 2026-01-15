import strawberry
from typing import AsyncIterator
from src.types import UserType, MessageType, CommentType, JSON
from src.resolvers.message_resolvers import (
    get_all_messages, get_message_by_id, create_message, 
    update_message, delete_message, create_comment
)
from src.resolvers.user_resolvers import (
    get_all_users, get_user_by_id, create_user, 
    update_user, delete_user
)

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL!"
    
    @strawberry.field
    async def messages(self) -> list[MessageType]:
        return await get_all_messages()
    
    @strawberry.field
    async def message(self, id: int) -> MessageType | None:
        return await get_message_by_id(id)
    
    @strawberry.field
    async def users(self) -> list[UserType]:
        return await get_all_users()
    
    @strawberry.field
    async def user(self, id: int) -> UserType | None:
        return await get_user_by_id(id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def test_mutation(self) -> str:
        return "Mutation works!"
    
    @strawberry.mutation
    async def create_message(
        self,
        author_id: int,
        content: str,
        title: str | None = None,
        metadata: JSON | None = None
    ) -> MessageType:
        return await create_message(author_id, content, title, metadata)
    
    @strawberry.mutation
    async def create_comment(
        self,
        message_id: int,
        author_id: int,
        content: str,
        parent_comment_id: int | None = None,
        metadata: JSON | None = None
    ) -> CommentType:
        return await create_comment(message_id, author_id, content, parent_comment_id, metadata)
    
    @strawberry.mutation
    async def update_message(
        self,
        message_id: int,
        title: str | None = None,
        content: str | None = None,
        metadata: JSON | None = None,
        stats: JSON | None = None
    ) -> MessageType | None:
        return await update_message(message_id, title, content, metadata, stats)
    
    @strawberry.mutation
    async def delete_message(self, message_id: int) -> bool:
        return await delete_message(message_id)
    
    @strawberry.mutation
    async def create_user(
        self,
        username: str,
        profile: JSON | None = None
    ) -> UserType:
        profile_dict = profile if isinstance(profile, dict) else None
        return await create_user(username, profile_dict)
    
    @strawberry.mutation
    async def update_user(
        self,
        user_id: int,
        username: str | None = None,
        profile: JSON | None = None
    ) -> UserType | None:
        profile_dict = profile if isinstance(profile, dict) else None
        return await update_user(user_id, username, profile_dict)
    
    @strawberry.mutation
    async def delete_user(self, user_id: int) -> bool:
        return await delete_user(user_id)

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def message_added(self) -> AsyncIterator[MessageType]:
        from pubsub import pubsub
        async for message_data in pubsub.subscribe("messages"):
            yield MessageType(**message_data)
    
    @strawberry.subscription
    async def comment_added(self, message_id: int) -> AsyncIterator[CommentType]:
        from pubsub import pubsub
        channel = f"comments:{message_id}"
        async for comment_data in pubsub.subscribe(channel):
            yield CommentType(**comment_data)
    
    @strawberry.subscription
    async def message_updated(self, message_id: int | None = None) -> AsyncIterator[MessageType]:
        from pubsub import pubsub
        if message_id:
            channel = f"message_updates:{message_id}"
        else:
            channel = "message_updates:all"
        async for message_data in pubsub.subscribe(channel):
            yield MessageType(**message_data)

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)