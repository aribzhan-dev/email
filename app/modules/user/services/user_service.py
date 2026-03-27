from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.user.models.user import User


async def create_user(db: AsyncSession, name: str) -> User:
    user = User(name=name)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()