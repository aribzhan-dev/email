from fastapi import APIRouter

from .chat_router import router as chat_router
from .message_router import router as message_router

router = APIRouter()

router.include_router(chat_router)
router.include_router(message_router)