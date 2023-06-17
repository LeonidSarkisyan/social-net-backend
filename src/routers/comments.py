from datetime import datetime
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
import src.models as models
import src.schemas
from src.database import get_db
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import json
import src.notifications as nt
from src.likesnoti import get_scheme_like_ws

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)


@router.get('/image')
def get_image():
    return FileResponse('static/utils/comment.png')


@router.post('/', response_model=src.schemas.Comment)
def create_comment(comment: src.schemas.CommentCreate, db: Session = Depends(get_db)):
    new_comment = models.Comment(
        text=comment.text,
        user_id=comment.user_id,
        post_id=comment.post_id,
        create_date_time=datetime.now()
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get('/{post_id}', response_model=list[src.schemas.Comment])
def get_comments_for_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    return post.comments


@router.put('/{comment_id}')
def update_comment(comment_id: int, new_text: str, db: Session = Depends(get_db)):
    comment = db.get(models.Comment, comment_id)
    comment.text = new_text
    db.commit()
    db.refresh(comment)
    return 'post is updated'


@router.delete('/{comment_id}')
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.get(models.Comment, comment_id)
    db.delete(comment)
    db.commit()
    return 'comment is deleted'


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_text(data)


manager = ConnectionManager()


@router.websocket('/ws/{profile_id}')
async def websocket_endpoint(websocket: WebSocket, profile_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                if data == '__ping__':
                    await manager.send_personal_message('__pong__', websocket)
                else:
                    if json.loads(data).get('type') == 'like':
                        data = json.loads(data)
                        print(data)
                        post = db.query(models.Post).filter(models.Post.id == data['post_id']).first()
                        if post:
                            new_like = models.Like(
                                user_id=data['user_id'],
                                post_id=data['post_id'],
                            )
                            db.add(new_like)
                            db.commit()
                            db.refresh(new_like)

                            data = get_scheme_like_ws(new_like)

                            if data['user_id'] != data['post']['profile_id']:
                                noti = nt.create_notification_like(data, db)
                                noti = json.dumps(noti, ensure_ascii=False)
                                await nt.wrire_message_id(noti, new_like.posts.profile_id)
                        else:
                            await manager.send_personal_message('error', websocket)
                    else:
                        data = json.loads(data)
                        post = db.query(models.Post).filter(models.Post.id == data['post_id']).first()
                        if post:
                            new_comment = models.Comment(
                                user_id=data['user_id'],
                                post_id=data['post_id'],
                                text=data['text'],
                                create_date_time=datetime.now()
                            )
                            db.add(new_comment)
                            db.commit()
                            db.refresh(new_comment)
                            data = {
                                "id": new_comment.id,
                                "text": new_comment.text,
                                "type": 'comment',
                                "create_date_time": new_comment.create_date_time.isoformat(),
                                "post_id": new_comment.post_id,
                                "user_id": new_comment.user_id,
                                "profile": {
                                    "id": new_comment.profile.id,
                                    "name": new_comment.profile.name,
                                    "surname": new_comment.profile.surname,
                                    "tag_name": new_comment.profile.tag_name
                                },
                                "post": {
                                    'profile_id': new_comment.post.profile_id
                                }
                            }
                            if data['user_id'] != data['post']['profile_id']:
                                noti = nt.create_notification(data, db)
                                noti = json.dumps(noti, ensure_ascii=False)
                                await nt.wrire_message_id(noti, new_comment.post.profile_id)
                            data = json.dumps(data, ensure_ascii=False)
                            await manager.broadcast(data)
                        else:
                            await manager.send_personal_message('error', websocket)

            except Exception as e:
                print(e)
                #await manager.send_personal_message('error', websocket)
                print('WebSocket не смог обработать запрос /131')

    except WebSocketDisconnect as e:
        print(e)
        print('Исправляемся!')
        manager.disconnect(websocket)