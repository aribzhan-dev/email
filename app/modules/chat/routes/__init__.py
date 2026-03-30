from fastapi import APIRouter

from .message_router import router as message_router
from .websocket import router as websocket_router

router = APIRouter()

router.include_router(message_router)
router.include_router(websocket_router)