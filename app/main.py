from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.router import message
from app.core.db import engine, Base
from app.services.email_reader import listen_for_emails_async


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(listen_for_emails_async())

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)
app.include_router(message.router)