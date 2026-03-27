from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_db
from app.modules.user.schemas.user import UserCreate, UserResponse
from app.modules.user.services.user_service import (
    create_user,
    get_user_by_id,
    get_users,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user_endpoint(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_user(db, data.name)


@router.get("/", response_model=List[UserResponse])
async def get_users_endpoint(
    db: AsyncSession = Depends(get_db),
):
    return await get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user