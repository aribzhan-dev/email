from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums.message_type import MessageType
from app.core.db import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type_enum"),
        default=MessageType.TEXT,
        nullable=False,
        index=True,
    )
    reply_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    chat = relationship(
        "app.modules.chat.models.chat.Chat",
        back_populates="messages",
    )
    sender = relationship(
        "app.modules.user.models.user.User",
        back_populates="sent_messages",
    )
    reply_to = relationship(
        "app.modules.chat.models.message.ChatMessage",
        remote_side=[id],
        backref="replies",
    )
    attachments = relationship(
        "app.modules.chat.models.attachment.ChatAttachment",
        back_populates="message",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ChatMessage id={self.id} chat_id={self.chat_id} "
            f"sender_id={self.sender_id} type={self.message_type}>"
        )