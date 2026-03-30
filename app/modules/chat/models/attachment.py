from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ChatAttachment(Base):
    __tablename__ = "chat_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)

    message_id: Mapped[int] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
    )

    path: Mapped[str] = mapped_column(String)
    mime: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)

    message = relationship(
        "app.modules.chat.models.message.ChatMessage",
        back_populates="attachments",
    )

    def __repr__(self) -> str:
        return f"<ChatAttachment id={self.id} file_name={self.file_name!r}>"