from pydantic import BaseModel
from datetime import datetime

class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True