import datetime
import json
from fastapi import WebSocket, APIRouter, Depends, WebSocketDisconnect
import src.models as models
import src.schemas
from src.database import get_db
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from src.oauth2 import get_current_user
from src.utils.users import get_profile


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.db = {}

    async def connect(self, websocket: WebSocket, profile_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.db[profile_id] = websocket

    def disconnect(self, websocket: WebSocket, profile_id: int):
        self.active_connections.remove(websocket)
        del self.db[profile_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_text(data)

    async def send_id_message(self, message: str, profile_id: int):
        print('qwerty', profile_id)
        websoket = self.db.get(profile_id)
        if websoket:
            await self.send_personal_message(message, websoket)
        else:
            print(f'websoсket: {websoket}\n')
            print(f'message: {message}\n'
                  f'profile_id: {profile_id}')
            print('Пользователя, кажется, нет в сети!')


notes = ConnectionManager()

router = APIRouter(
    tags=['notifications'],
    prefix='/notifications'
)


@router.websocket('/ws/{profile_id}')
async def create_websocket(websocket: WebSocket, profile_id: int, db: Session = Depends(get_db)):
    await notes.connect(websocket, profile_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                await notes.send_personal_message('__pong__', websocket)
            except Exception as e:
                print(e)
                print('WebSocket не смог обработать запрос /57')

    except WebSocketDisconnect:
        await notes.disconnect(websocket, profile_id)


async def write_all_messages(message: str):
    await notes.broadcast(message)


async def wrire_message_id(message: str, profile_id: int):
    print(message)
    print(profile_id)
    await notes.send_id_message(message, profile_id)


def create_notification(data, db: Session):
    print(data)
    new_noti = models.Notification(
        type=data['type'],
        comment_id=data['id'],
        profile_to_id=data['post']['profile_id'],
        date=datetime.datetime.now(),
        post_id=data['post_id']
    )
    db.add(new_noti)
    db.commit()
    db.refresh(new_noti)

    noti = {
        'id': new_noti.id,
        'type': new_noti.type,
        'comment': {
            'id': new_noti.comment.id,
            'text': new_noti.comment.text,
            'profile': {
                'id': new_noti.comment.profile.id,
                'tag_name': new_noti.comment.profile.tag_name,
                'name': new_noti.comment.profile.name,
                'surname': new_noti.comment.profile.surname
            },
            'post_id': new_noti.comment.post_id
        },
        'profile_to_id': new_noti.profile_to_id
    }

    return noti


def create_notification_like(data, db: Session):
    new_noti = models.Notification(
        type=data['type'],
        like_id=data['id'],
        profile_to_id=data['post']['profile_id'],
        date=datetime.datetime.now(),
        post_id=data['post_id']
    )
    db.add(new_noti)
    db.commit()
    db.refresh(new_noti)

    noti = {
        'id': new_noti.id,
        'type': new_noti.type,
        'like': {
            'id': new_noti.like.id,
            'profile': {
                'id': new_noti.like.profile.id,
                'tag_name': new_noti.like.profile.tag_name,
                'name': new_noti.like.profile.name,
                'surname': new_noti.like.profile.surname
            },
            'post_id': new_noti.like.post_id
        },
        'profile_to_id': new_noti.profile_to_id
    }

    return noti


def create_notification_request_friend(data: src.schemas.RequestFriend, db: Session):
    new_noti = models.Notification(
        type='requestfriend',
        request_friend_id=data.id,
        profile_to_id=data.profile_to_id,
        date=data.date
    )
    db.add(new_noti)
    db.commit()
    db.refresh(new_noti)


    noti = {
        "id": new_noti.id,
        "type": new_noti.type,
        "requestfriend": {
            "id": new_noti.request_friend.id,
            "accept": new_noti.request_friend.accept,
            "profile": {
                "id": new_noti.request_friend.profile_from.id,
                "name": new_noti.request_friend.profile_from.name,
                "surname": new_noti.request_friend.profile_from.surname,
                "tag_name": new_noti.request_friend.profile_from.tag_name,
            }
        }
    }
    print(f'Уведомление: {noti}')
    return noti


def create_notification_accept_friend(data: src.schemas.AcceptFriend, db: Session):
    new_noti  = models.Notification(
        type='acceptfriend',
        accept_friend_id=data.id,
        profile_to_id=data.who_send_id,
        date=datetime.datetime.now()
    )
    db.add(new_noti)
    db.commit()
    db.refresh(new_noti)
    noti = {
        'id': new_noti.id,
        'type': new_noti.type,
        'acceptfriend': {
            'id': new_noti.accept_friend.id,
            'profile': {
                'id': new_noti.accept_friend.who_accept.id,
                'name': new_noti.accept_friend.who_accept.name,
                'surname': new_noti.accept_friend.who_accept.surname,
                'tag_name': new_noti.accept_friend.who_accept.tag_name
            }
        }
    }
    return noti


@router.get('/{profile_id}', response_model=list[src.schemas.Notification])
def get_notifications(profile_id: int, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification)\
        .filter(models.Notification.profile_to_id == profile_id)\
        .order_by(models.Notification.date.desc())\
        .all()
    return notifications


@router.get('/image/new/no')
def get_image_no_new_noti():
    return FileResponse('static/utils/noti-no.png')


@router.get('/image/comment')
def get_image_comment_noti():
    return FileResponse('static/utils/comment2.png')


@router.get('/image/like')
def get_image_like_noti():
    return FileResponse('static/utils/heart.png')


@router.get('/image/requestfriend')
def get_image_request_friend_noti():
    return FileResponse('static/utils/add-friend.png')


@router.get('/image/newfriend')
def get_image_request_friend_noti():
    return FileResponse('static/utils/new-friend.png')


@router.get('/audio/file')
def get_audio():
    return FileResponse('static/audio/noti.mp3')


@router.get('/')
def write_all():
    print(notes.db)
    return 'good'


@router.get('/viewed/true')
def view_notifications(user: src.schemas.UserCreate = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_profile(user, db)
    notifications = db.query(models.Notification).filter(models.Notification.profile_to_id == profile.id).all()
    for notification in notifications:
        notification.viewed = True
        db.commit()
        db.refresh(notification)
    return 'Уведомления просмотрены!'
