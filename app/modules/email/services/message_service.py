import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import UploadFile
from app.modules.email.models import EmailAttachment
from app.core.config import get_settings
from app.modules.email.models.message import EmailMessage
from app.modules.email.services.email_service import send_email

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

    email_message = EmailMessage(
        sender_email=settings.SMTP_USER,
        receiver_email=receiver_email,
        subject=subject,
        body=body,
    )
    db.add(email_message)
    await db.flush()

    saved_files = []
    for file in files:
        if not file or not file.filename:
            continue

        file_path = os.path.join(UPLOAD_DIR, f"{email_message.id}_{file.filename}")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        attachment = EmailAttachment(
            message_id=email_message.id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file.content_type or "application/octet-stream",
            file_size=len(content),
        )

        db.add(attachment)
        saved_files.append(file_path)

    await db.commit()
    await db.refresh(email_message)

    await send_email(
        to_email=receiver_email,
        subject=subject,
        body=body,
        file_paths=saved_files,
    )

    return email_message


async def get_messages(
    db: AsyncSession,
    email: str,
    filter: str = "all",
):
    if filter == "sent":
        condition = EmailMessage.sender_email == email
    elif filter == "received":
        condition = EmailMessage.receiver_email == email
    else:
        condition = or_(
            EmailMessage.sender_email == email,
            EmailMessage.receiver_email == email,
        )

    result = await db.execute(
        select(EmailMessage)
        .where(condition)
        .order_by(EmailMessage.created_at.desc())
    )
    return result.scalars().all()