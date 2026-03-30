from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.modules.chat.schemas.chat import (
    ChatCreate, ChatResponse,
    ChatListItem, ChatListResponse,
    LastMessage
)
from app.modules.chat.services.chat_service import create_chat, get_user_chats
from app.modules.chat.schemas.group import (
    CreateGroupSchema,
    AddUserSchema,
    RemoveUserSchema,
)
from app.modules.chat.services.group_service import (
    create_group,
    add_user_to_group,
    remove_user_from_group,
)
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
    mark_messages_as_seen
)

from app.modules.chat.utils.mapper import map_to_response

router = APIRouter(prefix="", tags=["Whatsapp"])


@router.post("/chat/create", response_model=ChatResponse)
async def create_chat_endpoint(
    data: ChatCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_chat(
        db=db,
        user_ids=data.user_ids,
        is_group=data.is_group,
    )


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



@router.post("/group/create")
async def create_group_endpoint(
    creator_id: int,
    data: CreateGroupSchema,
    db: AsyncSession = Depends(get_db),
):
    return await create_group(
        db,
        name=data.name,
        creator_id=creator_id,
        user_ids=data.user_ids,
    )


# ➕ ADD USER
@router.post("/group/{chat_id}/add-user")
async def add_user(
    chat_id: int,
    data: AddUserSchema,
    db: AsyncSession = Depends(get_db),
):
    return await add_user_to_group(db, chat_id, data.user_id)


@router.post("/group/{chat_id}/remove-user")
async def remove_user(
    chat_id: int,
    data: RemoveUserSchema,
    db: AsyncSession = Depends(get_db),
):
    return await remove_user_from_group(db, chat_id, data.user_id)




@router.post("/message/seen")
async def seen_messages(
    chat_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    await mark_messages_as_seen(db, chat_id, user_id)
    return {"status": "seen updated"}




@router.get("/chats", response_model=ChatListResponse)
async def get_chats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    chats = await get_user_chats(db, user_id)

    result = []

    for chat in chats:
        last = chat["last_message"]

        result.append(ChatListItem(
            chat_id=chat["chat_id"],
            is_group=chat["is_group"],
            unread_count=chat["unread_count"],
            last_message=LastMessage(
                id=last.id,
                text=last.text,
                type=last.message_type,
                sender_id=last.sender_id,
                created_at=last.created_at,
            ) if last else None
        ))

    return {"chats": result}

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


