from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.modules.chat.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    await manager.connect(chat_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)