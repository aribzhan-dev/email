from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

from app.modules.chat.schemas.message import (
    SendMessageSchema,
    SendMediaSchema,
    MessageResponse,
    PaginatedMessageResponse,
)

from app.modules.chat.services.message_service import (
    send_message,
    send_media,
    get_chat_messages,
    update_message,
    delete_message,
)

from app.modules.chat.utils.mapper import map_to_response

router = APIRouter(prefix="/messages", tags=["Whatsapp"])


@router.post("/send", response_model=MessageResponse)
async def send_text_message(
    chat_id: int,
    sender_id: int,
    data: SendMessageSchema,
    db: AsyncSession = Depends(get_db),
):
    message = await send_message(db, chat_id, sender_id, data)
    return map_to_response(message)


@router.post("/send-media", response_model=MessageResponse)
async def send_media_message(
    chat_id: int,
    sender_id: int,
    data: SendMediaSchema,
    db: AsyncSession = Depends(get_db),
):
    message = await send_media(db, chat_id, sender_id, data)
    return map_to_response(message)


@router.get("/{chat_id}", response_model=PaginatedMessageResponse)
async def get_messages(
    chat_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await get_chat_messages(db, chat_id, page, limit)

    return {
        "items": [map_to_response(m) for m in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"],
    }


@router.put("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: int,
    text: str,
    db: AsyncSession = Depends(get_db),
):
    message = await update_message(db, message_id, text)
    return map_to_response(message)



@router.delete("/{message_id}")
async def remove_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await delete_message(db, message_id)