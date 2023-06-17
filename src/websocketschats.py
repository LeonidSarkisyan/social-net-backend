import datetime
import json
from src.utils import messages as msg
from fastapi import APIRouter, Depends, UploadFile, Form, File, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy import or_, and_
from src.utils import chats as chats_utils
import src.models as models
import src.schemas
from sqlalchemy.orm import Session
from src.database import get_db
import src.messagenotifications as msg_notification

router = APIRouter(
    prefix='/websocket',
    tags=['websocket']
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.db = {}

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.db[chat_id] = websocket

    def disconnect(self, websocket: WebSocket, chat_id: int):
        self.active_connections.remove(websocket)
        del self.db[chat_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_text(data)

    async def send_id_message(self, message: str, chat_id: int):
        websoket = self.db.get(chat_id)
        if websoket:
            await self.send_personal_message(message, websoket)


connections = ConnectionManager()


@router.websocket('/typing/{profile_id}')
async def create_connect(websocket: WebSocket, profile_id: int, db: Session = Depends(get_db)):
    await connections.connect(websocket, profile_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == '__ping__':
                await connections.send_id_message('__pong__', profile_id)
            elif json.loads(data).get('type') == '__typing__':
                data = json.loads(data)
                await connections.send_id_message(json.dumps(data, ensure_ascii=False), data['profile_to_id'])
    except WebSocketDisconnect:
        connections.disconnect(websocket, profile_id)