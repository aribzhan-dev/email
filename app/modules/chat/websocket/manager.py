from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket):
        await websocket.accept()

        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []

        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket):
        self.active_connections[chat_id].remove(websocket)

        if not self.active_connections[chat_id]:
            del self.active_connections[chat_id]

    async def send_to_chat(self, chat_id: int, data: dict):
        if chat_id not in self.active_connections:
            return

        for connection in self.active_connections[chat_id]:
            await connection.send_json(data)


manager = ConnectionManager()