from fastapi import APIRouter

from .message import router as email_router

router = APIRouter()
router.include_router(email_router)