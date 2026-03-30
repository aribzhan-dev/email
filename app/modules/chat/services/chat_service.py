from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from app.modules.chat.models.chat import Chat
from app.modules.chat.models.chat_member import ChatMember
from app.modules.user.models.user import User
from app.modules.chat.models.message import ChatMessage

async def create_chat(
    db: AsyncSession,
    user_ids: list[int],
    is_group: bool = False,
):
    if not is_group:
        return await get_or_create_private_chat(db, user_ids)

    chat = Chat(is_group=True)
    db.add(chat)
    await db.flush()

    for user_id in user_ids:
        db.add(ChatMember(chat_id=chat.id, user_id=user_id))

    await db.commit()
    await db.refresh(chat)

    return chat


async def get_or_create_private_chat(
    db: AsyncSession,
    user_ids: list[int],
):
    if len(user_ids) != 2:
        raise HTTPException(400, "Private chat faqat 2 user bo‘ladi")

    user1, user2 = user_ids
    subquery = (
        select(ChatMember.chat_id)
        .where(ChatMember.user_id.in_(user_ids))
        .group_by(ChatMember.chat_id)
        .having(func.count(ChatMember.user_id) == 2)
    )

    result = await db.execute(
        select(Chat)
        .where(
            Chat.id.in_(subquery),
            Chat.is_group == False
        )
    )

    existing_chat = result.scalars().first()

    if existing_chat:
        return existing_chat

    chat = Chat(is_group=False)
    db.add(chat)
    await db.flush()

    for user_id in user_ids:
        db.add(ChatMember(chat_id=chat.id, user_id=user_id))

    await db.commit()
    await db.refresh(chat)

    return chat



async def get_user_chats(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Chat)
        .join(ChatMember, ChatMember.chat_id == Chat.id)
        .where(ChatMember.user_id == user_id)
    )

    chats = result.scalars().all()

    response = []

    for chat in chats:
        last_msg_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        last_message = last_msg_result.scalar_one_or_none()

        unread_result = await db.execute(
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.chat_id == chat.id,
                ChatMessage.sender_id != user_id,
                ChatMessage.is_seen == False,
            )
        )
        unread_count = unread_result.scalar() or 0

        response.append({
            "chat_id": chat.id,
            "is_group": chat.is_group,
            "last_message": last_message,
            "unread_count": unread_count,
        })

    return response