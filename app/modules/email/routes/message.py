from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_db
from app.modules.email.schemas.message import MessageResponse
from app.modules.email.services.message_service import send_message, get_messages


router = APIRouter(prefix="", tags=["Emails"])


@router.post("/send", response_model=MessageResponse)
async def send_message_endpoint(
    receiver_email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    db: AsyncSession = Depends(get_db),
    file1: UploadFile = File(default=None),
    file2: UploadFile = File(default=None),
    file3: UploadFile = File(default=None),
):
    files = [f for f in [file1, file2, file3] if f and f.filename]

    return await send_message(
        db=db,
        receiver_email=receiver_email,
        subject=subject,
        body=body,
        files=files,
    )


@router.get("/messages", response_model=List[MessageResponse])
async def get_messages_endpoint(
    email: str,
    filter: str = "all",
    db: AsyncSession = Depends(get_db),
):
    return await get_messages(db=db, email=email, filter=filter)