from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.modules.chat.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, user_id: int):
    await manager.connect(chat_id, user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "typing":
                await manager.send_to_chat(
                    chat_id,
                    {
                        "type": "typing",
                        "user_id": user_id,
                        "is_typing": data.get("is_typing", False),
                    },
                )

    except:
        manager.disconnect(chat_id, user_id, websocket)