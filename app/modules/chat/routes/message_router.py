from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.modules.chat.services.message_service import send_message, get_chat_messages, update_message, delete_message
from app.modules.chat.schemas.message import MessageResponse


router = APIRouter(prefix="/messages", tags=["Chat Messages"])


@router.post("/send", response_model=MessageResponse)
async def send_message_endpoint(
    chat_id: int = Form(...),
    sender_id: int = Form(...),
    text: Optional[str] = Form(None),
    reply_to_id: Optional[int] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
):
    return await send_message(
        db=db,
        chat_id=chat_id,
        sender_id=sender_id,
        text=text,
        files=files,
        reply_to_id=reply_to_id,
    )


@router.get("/{chat_id}", response_model=List[MessageResponse])
async def get_messages_endpoint(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_chat_messages(db, chat_id)


@router.put("/{message_id}")
async def update_message_endpoint(
    message_id: int,
    new_text: str = Body(...),
    db: AsyncSession = Depends(get_db),
):
    return await update_message(db, message_id, new_text)


@router.delete("/{message_id}")
async def delete_message_endpoint(
    message_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await delete_message(db, message_id)