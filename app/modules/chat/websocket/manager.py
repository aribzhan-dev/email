from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.chat_connections: Dict[int, List[WebSocket]] = {}
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.online_users: Dict[int, bool] = {}


    async def connect(self, chat_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()

        self.chat_connections.setdefault(chat_id, []).append(websocket)
        self.user_connections.setdefault(user_id, []).append(websocket)
        self.online_users[user_id] = True

        await self.broadcast_user_status(user_id, True)


    async def disconnect(self, chat_id: int, user_id: int, websocket: WebSocket):
        if chat_id in self.chat_connections:
            if websocket in self.chat_connections[chat_id]:
                self.chat_connections[chat_id].remove(websocket)

            if not self.chat_connections[chat_id]:
                del self.chat_connections[chat_id]

        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)

            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

                self.online_users[user_id] = False

                await self.broadcast_user_status(user_id, False)


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


    async def broadcast_user_status(self, user_id: int, is_online: bool):
        for connections in self.chat_connections.values():
            for ws in connections:
                await ws.send_json({
                    "type": "user_status",
                    "user_id": user_id,
                    "is_online": is_online,
                })


manager = ConnectionManager()