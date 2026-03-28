from app.modules.files.routes.file_routes import router as file_router
from fastapi import APIRouter
router = APIRouter()

router.include_router(file_router)