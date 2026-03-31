from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from app.modules.chat.models.chat import Chat
from app.modules.chat.models.chat_member import ChatMember
from app.modules.chat.websocket import manager


async def create_group(
    db: AsyncSession,
    name: str,
    creator_id: int,
    user_ids: list[int],
):
    chat = Chat(
        is_group=True,
        name=name,
    )

    db.add(chat)
    await db.flush()

    all_users = set(user_ids + [creator_id])

    for user_id in all_users:
        db.add(ChatMember(chat_id=chat.id, user_id=user_id))

    await db.commit()
    return chat


async def add_user_to_group(db, chat_id, user_id):
    chat = await db.get(Chat, chat_id)
    if not chat or not chat.is_group:
        raise HTTPException(404, "Group not found")

    db.add(ChatMember(chat_id=chat_id, user_id=user_id))
    await db.commit()

    await manager.send_to_chat(
        chat_id,
        {
            "type": "group_update",
            "event": "user_added",
            "chat_id": chat_id,
            "user_id": user_id,
        },
    )

    return {"status": "user added"}


async def remove_user_from_group(
    db: AsyncSession,
    chat_id: int,
    user_id: int,
):
    result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == user_id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(404, "User not in group")

    await db.delete(member)
    await db.commit()

    await manager.send_to_chat(
        chat_id,
        {
            "type": "group_update",
            "event": "user_removed",
            "chat_id": chat_id,
            "user_id": user_id,
        },
    )

    return {"status": "user removed"}