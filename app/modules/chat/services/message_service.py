from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import UploadFile, HTTPException

from app.modules.chat.models.message import ChatMessage
from app.modules.chat.models.chat import Chat
from app.modules.chat.models.attachment import ChatAttachment
from app.common.enums.message_type import MessageType
from app.common.utils.file import save_file

async def send_message(
    db: AsyncSession,
    chat_id: int,
    sender_id: int,
    text: Optional[str],
    files: Optional[List[UploadFile]] = None,
    reply_to_id: Optional[int] = None,
):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if reply_to_id:
        reply_msg = await db.get(ChatMessage, reply_to_id)
        if not reply_msg:
            raise HTTPException(status_code=404, detail="Reply message not found")

    message_type = MessageType.TEXT

    if files:
        content_type = files[0].content_type or ""
        if content_type.startswith("image"):
            message_type = MessageType.IMAGE
        elif content_type.startswith("video"):
            message_type = MessageType.VIDEO
        elif content_type.startswith("audio"):
            message_type = MessageType.AUDIO
        else:
            message_type = MessageType.FILE

    chat_message = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        text=text,
        message_type=message_type,
        reply_to_id=reply_to_id,
    )

    db.add(chat_message)
    await db.flush()

    if files:
        for file in files:
            file_path, file_name, file_type, file_size = await save_file(file)

            chat_attachment = ChatAttachment(
                message_id=chat_message.id,
                file_name=file_name,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
            )

            db.add(chat_attachment)

    await db.commit()
    await db.refresh(chat_message)

    return chat_message


async def get_chat_messages(
    db: AsyncSession,
    chat_id: int,
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
    )

    return result.scalars().all()


async def update_message(
    db: AsyncSession,
    message_id: int,
    new_text: str,
):
    chat_message = await db.get(ChatMessage, message_id)

    if not chat_message:
        raise HTTPException(404, "Message not found")

    chat_message.text = new_text

    await db.commit()
    await db.refresh(chat_message)

    return chat_message



async def delete_message(
    db: AsyncSession,
    message_id: int,
):
    chat_message = await db.get(ChatMessage, message_id)

    if not chat_message:
        raise HTTPException(404, "Message not found")

    await db.delete(chat_message)
    await db.commit()

    return {"detail": "Message deleted"}
