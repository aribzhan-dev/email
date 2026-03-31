from pydantic import BaseModel
from typing import List


class CreateGroupSchema(BaseModel):
    name: str
    user_ids: List[int]


class AddUserSchema(BaseModel):
    user_id: int


class RemoveUserSchema(BaseModel):
    user_id: int