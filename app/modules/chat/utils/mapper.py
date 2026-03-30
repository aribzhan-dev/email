from app.modules.chat.models.message import ChatMessage
from app.modules.chat.schemas.message import MessageResponse, Media


def map_to_response(message: ChatMessage) -> MessageResponse:
    media = None

    if message.attachments:
        file = message.attachments[0]
        media = Media(
            url=file.path,
            mime=file.mime,
            name=file.name,
            size=file.size,
        )

    return MessageResponse(
        id=message.id,
        chat_id=message.chat_id,
        type=message.message_type,
        text=message.text,
        media=media,
        sender_id=message.sender_id,
        timestamp=message.created_at,
        is_seen=message.is_seen,
        seen_at=message.seen_at,
    )