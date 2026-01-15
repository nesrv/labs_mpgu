import json
from database import AsyncSessionLocal
from sqlalchemy import text
from src.types import UserType

async def get_all_users() -> list[UserType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users ORDER BY id")
        )
        rows = result.mappings().all()
        return [UserType(**row) for row in rows]

async def get_user_by_id(user_id: int) -> UserType | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {"id": user_id}
        )
        row = result.mappings().first()
        return UserType(**row) if row else None

async def create_user(username: str, profile: dict | None = None) -> UserType:
    async with AsyncSessionLocal() as session:
        profile_json = json.dumps(profile) if profile else '{}'
        
        result = await session.execute(
            text("""
                INSERT INTO users (username, profile)
                VALUES (:username, CAST(:profile AS jsonb))
                RETURNING *
            """),
            {
                "username": username,
                "profile": profile_json
            }
        )
        await session.commit()
        
        row = result.mappings().first()
        return UserType(**row) if row else None

async def update_user(
    user_id: int,
    username: str | None = None,
    profile: dict | None = None
) -> UserType | None:
    async with AsyncSessionLocal() as session:
        updates = []
        params = {"id": user_id}
        
        if username is not None:
            updates.append("username = :username")
            params["username"] = username
        
        if profile is not None:
            updates.append("profile = CAST(:profile AS jsonb)")
            params["profile"] = json.dumps(profile)
        
        if not updates:
            return await get_user_by_id(user_id)
        
        result = await session.execute(
            text(f"""
                UPDATE users
                SET {', '.join(updates)}
                WHERE id = :id
                RETURNING *
            """),
            params
        )
        await session.commit()
        
        row = result.mappings().first()
        return UserType(**row) if row else None

async def delete_user(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM users WHERE id = :id RETURNING id"),
            {"id": user_id}
        )
        await session.commit()
        return result.rowcount > 0