from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.modules.chat.schemas.chat import ChatCreate, ChatResponse
from app.modules.chat.services.chat_service import create_chat


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/create", response_model=ChatResponse)
async def create_chat_endpoint(
    data: ChatCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_chat(
        db=db,
        user_ids=data.user_ids,
        is_group=data.is_group,
    )