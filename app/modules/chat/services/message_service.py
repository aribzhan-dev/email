from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from fastapi import HTTPException

from app.modules.chat.models.message import ChatMessage
from app.modules.chat.models.chat import Chat
from app.modules.chat.models.attachment import ChatAttachment
from app.modules.chat.websocket.manager import manager
from app.modules.chat.schemas.message import SendMessageSchema, SendMediaSchema
from app.common.enums.message_type import MessageType


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
        raise HTTPException(status_code=404, detail="Chat not found")

    reply_to_id = data.reply_to if data.reply_to else None

    if reply_to_id is not None:
        reply_message = await db.get(ChatMessage, reply_to_id)
        if not reply_message:
            raise HTTPException(status_code=400, detail="Reply message not found")
        if reply_message.chat_id != chat_id:
            raise HTTPException(status_code=400, detail="Reply message belongs to another chat")

    message = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        text=data.text,
        message_type=MessageType.TEXT,
        reply_to_id=data.reply_to if data.reply_to else None,
        mentions=data.mentions or [],
    )

    db.add(message)
    await db.commit()

    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.attachments))
        .where(ChatMessage.id == message.id)
    )
    message = result.scalar_one()

    await manager.send_to_chat(
        chat_id,
        {
            "event": "message:new",
            "id": message.id,
            "chat_id": message.chat_id,
            "text": message.text,
            "type": message.message_type.value,
            "sender_id": message.sender_id,
            "is_seen": message.is_seen,
            "seen_at": message.seen_at.isoformat() if message.seen_at else None,
            "media": None,
            "timestamp": message.created_at.isoformat(),
        },
    )

    return message


async def send_media(
    db: AsyncSession,
    chat_id: int,
    sender_id: int,
    data: SendMediaSchema,
):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    reply_to_id = data.reply_to if data.reply_to else None

    if reply_to_id is not None:
        reply_message = await db.get(ChatMessage, reply_to_id)
        if not reply_message:
            raise HTTPException(status_code=400, detail="Reply message not found")
        if reply_message.chat_id != chat_id:
            raise HTTPException(status_code=400, detail="Reply message belongs to another chat")

    message = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        text=data.text,
        message_type=MessageType.TEXT,
        reply_to_id=data.reply_to if data.reply_to else None,
        mentions=data.mentions or [],
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

    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.attachments))
        .where(ChatMessage.id == message.id)
    )
    message = result.scalar_one()

    file = message.attachments[0] if message.attachments else None

    await manager.send_to_chat(
        chat_id,
        {
            "event": "message:new",
            "id": message.id,
            "chat_id": message.chat_id,
            "text": message.text,
            "type": message.message_type.value,
            "sender_id": message.sender_id,
            "is_seen": message.is_seen,
            "seen_at": message.seen_at.isoformat() if message.seen_at else None,
            "media": {
                "url": file.path,
                "mime": file.mime,
                "name": file.name,
                "size": file.size,
            } if file else None,
            "timestamp": message.created_at.isoformat(),
        },
    )

    if data.mentions:
        for user_id in data.mentions:
            await manager.send_to_user(
                user_id,
                {
                    "type": "mention",
                    "chat_id": chat_id,
                    "message_id": message.id,
                    "from_user": sender_id,
                },
            )

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
    total = total_result.scalar() or 0

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
        raise HTTPException(status_code=404, detail="Message not found")

    message.text = new_text
    await db.commit()

    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.attachments))
        .where(ChatMessage.id == message.id)
    )
    message = result.scalar_one()

    await manager.send_to_chat(
        message.chat_id,
        {
            "event": "message:updated",
            "id": message.id,
            "chat_id": message.chat_id,
            "text": message.text,
            "type": message.message_type.value,
            "sender_id": message.sender_id,
            "is_seen": message.is_seen,
            "seen_at": message.seen_at.isoformat() if message.seen_at else None,
            "timestamp": message.created_at.isoformat(),
        },
    )

    return message


async def delete_message(
    db: AsyncSession,
    message_id: int,
):
    message = await db.get(ChatMessage, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    chat_id = message.chat_id

    await db.delete(message)
    await db.commit()

    await manager.send_to_chat(
        chat_id,
        {
            "event": "message:deleted",
            "id": message_id,
            "chat_id": chat_id,
        },
    )

    return {"detail": "Message deleted"}


async def mark_messages_as_seen(
    db: AsyncSession,
    chat_id: int,
    user_id: int,
):
    now = datetime.now(timezone.utc)

    await db.execute(
        update(ChatMessage)
        .where(
            ChatMessage.chat_id == chat_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.is_seen.is_(False),
        )
        .values(
            is_seen=True,
            seen_at=now,
        )
    )

    await db.commit()

    await manager.send_to_chat(
        chat_id,
        {
            "event": "message:seen",
            "chat_id": chat_id,
            "user_id": user_id,
            "seen_at": now.isoformat(),
        },
    )