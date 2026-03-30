from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    is_group: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    members = relationship(
        "app.modules.chat.models.chat_member.ChatMember",
        back_populates="chat",
        cascade="all, delete-orphan",
    )
    messages = relationship(
        "app.modules.chat.models.message.ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at.asc()"
    )

    def __repr__(self) -> str:
        return f"<Chat id={self.id} is_group={self.is_group}>"