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
import src.websocketschats as WSC


router = APIRouter(
    prefix='/chats',
    tags=['chats']
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
        #print('qwerty', chat_id)
        websoket = self.db.get(chat_id)
        #print(websoket)
        if websoket:
            await self.send_personal_message(message, websoket)
        #else:
            #print(f'websoсket: {websoket}\n')
            #print(f'message: {message}\n'
            #      f'chat_id: {chat_id}')
            #print('Пользователя, кажется, нет в сети!')


connection_chats = ConnectionManager()


@router.get('/{profile_id}', response_model=list[src.schemas.Chat])
def get_list_chats(profile_id: int, db: Session = Depends(get_db)):
    chats = db.query(models.Chat).filter(
        or_(
            models.Chat.profile_first_id == profile_id,
            models.Chat.profile_second_id == profile_id
        )
    ).order_by(models.Chat.datetime_create.desc()).all()
    for index, chat in enumerate(chats):
        chats[index].messages = chats[index].messages[-20:]
    return chats


@router.get('/simple/{profile_id}', response_model=list[src.schemas.ChatSimple])
def get_list_chats_simple(profile_id: int, db: Session = Depends(get_db)):
    chats = db.query(models.Chat).filter(
        or_(
            models.Chat.profile_first_id == profile_id,
            models.Chat.profile_second_id == profile_id
        )
    ).order_by(models.Chat.datetime_create.desc()).all()
    return chats


@router.websocket('/ws/{profile_id}')
async def create_connection(websocket: WebSocket, profile_id: int, db: Session = Depends(get_db)):
    await connection_chats.connect(websocket, profile_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == '__ping__':
                await connection_chats.send_id_message('__pong__', profile_id)
            #elif json.loads(data).get('type') == '__typing__':
            #    print('Печатает бля!')
            #    data = json.loads(data)
            #    print(data)
            #    print(data['profile_to_id'])
            #    await connection_chats.send_id_message(json.dumps(data, ensure_ascii=False), data['profile_to_id'])
            else:
                data = json.loads(data)
                message = msg.create_message(data, profile_id, db)
                await msg_notification.notify_about_message(data, profile_id, db)
                await connection_chats.broadcast(json.dumps(message, ensure_ascii=False))
    except WebSocketDisconnect:
        connection_chats.disconnect(websocket, profile_id)


@router.post('/')
def create_chat(request: src.schemas.ChatCreate, db: Session = Depends(get_db)):
    chat = chats_utils.is_chat_exist(request, db)
    if chat is None:
        chat = chats_utils.create_chat(request, db)
    return chat


@router.get('/get/webs')
def get():
    print(connection_chats.db)
    return 'good'