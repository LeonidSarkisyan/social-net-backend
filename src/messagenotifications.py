from fastapi import Depends, APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from src.database import get_db
import src.schemas
import src.models as models
import json

router = APIRouter(
    prefix='/message/notification',
    tags=['message notification']
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
        websocket = self.db.get(chat_id)
        if websocket:
            await self.send_personal_message(message, websocket)


messages_notification_manager = ConnectionManager()


@router.websocket('/ws/{profile_id}')
async def create_websocket(websocket: WebSocket, profile_id: int, db: Session = Depends(get_db)):
    await messages_notification_manager.connect(websocket, profile_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == '__ping__':
                await messages_notification_manager.send_id_message('__pong__', profile_id)
            else:
                data = json.loads(data)
                # await messages_notification_manager.broadcast(json.dumps(message, ensure_ascii=False))
    except WebSocketDisconnect:
        messages_notification_manager.disconnect(websocket, profile_id)


@router.get('/')
def test():
    return messages_notification_manager.db


async def notify_about_message(data: dict, profile_id: int, db: Session):
    await messages_notification_manager.send_id_message(json.dumps(data, ensure_ascii=False), data['profile_to_id'])