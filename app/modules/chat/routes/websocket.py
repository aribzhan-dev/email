from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.modules.chat.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, user_id: int):
    await manager.connect(chat_id, user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(chat_id, user_id, websocket)