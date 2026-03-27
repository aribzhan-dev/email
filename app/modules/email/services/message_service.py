import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import UploadFile
from app.models.attachment import Attachment
from app.core.config import get_settings
from app.models.message import Message
from app.services.email_service import send_email

UPLOAD_DIR = "uploads"


async def send_message(
    db: AsyncSession,
    receiver_email: str,
    subject: str,
    body: str,
    files: List[UploadFile],
):
    settings = get_settings()
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    message = Message(
        sender_email=settings.SMTP_USER,
        receiver_email=receiver_email,
        subject=subject,
        body=body,
    )
    db.add(message)
    await db.flush()

    saved_files = []
    for file in files:
        if not file or not file.filename:
            continue

        file_path = os.path.join(UPLOAD_DIR, f"{message.id}_{file.filename}")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        attachment = Attachment(
            message_id=message.id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file.content_type or "application/octet-stream",
            file_size=len(content),
        )

        db.add(attachment)
        saved_files.append(file_path)

    await db.commit()
    await db.refresh(message)

    await send_email(
        to_email=receiver_email,
        subject=subject,
        body=body,
        file_paths=saved_files,
    )

    return message


async def get_messages(
    db: AsyncSession,
    email: str,
    filter: str = "all",
):
    if filter == "sent":
        condition = Message.sender_email == email
    elif filter == "received":
        condition = Message.receiver_email == email
    else:
        condition = or_(
            Message.sender_email == email,
            Message.receiver_email == email,
        )

    result = await db.execute(
        select(Message)
        .where(condition)
        .order_by(Message.created_at.desc())
    )
    return result.scalars().all()