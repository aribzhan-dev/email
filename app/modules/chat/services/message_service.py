from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from fastapi import HTTPException

from app.modules.chat.models.message import ChatMessage
from app.modules.chat.models.chat import Chat
from app.modules.chat.models.attachment import ChatAttachment

from app.modules.chat.schemas.message import (
    SendMessageSchema,
    SendMediaSchema,
)

from app.common.enums.message_type import MessageType


# 🔥 HELPER
def detect_type(mime: str) -> MessageType:
    if mime.startswith("image"):
        return MessageType.IMAGE
    elif mime.startswith("video"):
        return MessageType.VIDEO
    elif mime.startswith("audio"):
        return MessageType.AUDIO
    else:
        return MessageType.FILE



async def send_message(
    db: AsyncSession,
    chat_id: int,
    sender_id: int,
    data: SendMessageSchema,
):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")

    message = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        text=data.text,
        message_type=MessageType.TEXT,
        reply_to_id=data.reply_to if data.reply_to else None,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


async def send_media(
    db: AsyncSession,
    chat_id: int,
    sender_id: int,
    data: SendMediaSchema,
):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")

    message = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        text=data.caption,
        message_type=detect_type(data.mime),
        reply_to_id=data.reply_to if data.reply_to else None,
    )

    db.add(message)
    await db.flush()

    attachment = ChatAttachment(
        message_id=message.id,
        path=data.url,
        mime=data.mime,
        name=data.file_name,
        size=data.size,
    )

    db.add(attachment)

    await db.commit()
    await db.refresh(message)

    return message


async def get_chat_messages(
    db: AsyncSession,
    chat_id: int,
    page: int = 1,
    limit: int = 20,
):
    if page < 1:
        page = 1

    if limit > 100:
        limit = 100

    offset = (page - 1) * limit
    total_result = await db.execute(
        select(func.count()).select_from(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.attachments))
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    messages = result.scalars().all()

    return {
        "items": messages,
        "total": total,
        "page": page,
        "limit": limit,
    }



async def update_message(
    db: AsyncSession,
    message_id: int,
    new_text: str,
):
    message = await db.get(ChatMessage, message_id)

    if not message:
        raise HTTPException(404, "Message not found")

    message.text = new_text

    await db.commit()
    await db.refresh(message)

    return message



async def delete_message(
    db: AsyncSession,
    message_id: int,
):
    message = await db.get(ChatMessage, message_id)

    if not message:
        raise HTTPException(404, "Message not found")

    await db.delete(message)
    await db.commit()

    return {"detail": "Message deleted"}