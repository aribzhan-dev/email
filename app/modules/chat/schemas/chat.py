from pydantic import BaseModel
from typing import List


class ChatCreate(BaseModel):
    user_ids: List[int]
    is_group: bool = False


class ChatResponse(BaseModel):
    id: int
    is_group: bool

    class Config:
        from_attributes = True