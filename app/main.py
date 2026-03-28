from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from app.modules.email.routes import router as email_router
from app.modules.chat.routes import router as chat_router
from app.modules.email.services.listener import start_email_listener
from app.modules.user.routes import router as user_router
from app.core.config import get_settings
from app.modules.files.routes import router as file_router

settings = get_settings()



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App starting...")
    asyncio.create_task(start_email_listener())

    yield

    print("🛑 App shutting down...")


app = FastAPI(
    title="Inbox System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(user_router, prefix="/api")
app.include_router(file_router, prefix="/api")
app.include_router(email_router, prefix="/api/email")
app.include_router(chat_router, prefix="/api/whatsapp")


@app.get("/")
async def root():
    return {"status": "ok"}