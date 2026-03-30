from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.chat_connections: Dict[int, List[WebSocket]] = {}
        self.user_connections: Dict[int, List[WebSocket]] = {}


    async def connect(self, chat_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()

        if chat_id not in self.chat_connections:
            self.chat_connections[chat_id] = []

        self.chat_connections[chat_id].append(websocket)

        if user_id not in self.user_connections:
            self.user_connections[user_id] = []

        self.user_connections[user_id].append(websocket)

    def disconnect(self, chat_id: int, user_id: int, websocket: WebSocket):
        if chat_id in self.chat_connections:
            self.chat_connections[chat_id].remove(websocket)

            if not self.chat_connections[chat_id]:
                del self.chat_connections[chat_id]

        if user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)

            if not self.user_connections[user_id]:
                del self.user_connections[user_id]


    async def send_to_chat(self, chat_id: int, data: dict):
        if chat_id not in self.chat_connections:
            return

        for ws in self.chat_connections[chat_id]:
            await ws.send_json(data)

    async def send_to_user(self, user_id: int, data: dict):
        if user_id not in self.user_connections:
            return

        for ws in self.user_connections[user_id]:
            await ws.send_json(data)


manager = ConnectionManager()