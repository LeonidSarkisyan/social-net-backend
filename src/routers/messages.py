import json

from fastapi import APIRouter, Depends, UploadFile, Form, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.oauth2 import get_current_user
from src.utils.users import get_profile
from src.database import get_db
from fastapi.responses import FileResponse
from src.utils.messages import update_message as update_msg, delete_message as delete_msg
from src.websocketschats import connections as WSC
import src.models as models
import src.schemas

router = APIRouter(
    prefix='/messages',
    tags=['messages']
)


@router.post('/')
def create_message(request: src.schemas.MessageCreate, db: Session = Depends(get_db)):
    new_message = models.Message(
        chat_id=request.chat_id,
        profile_from_id=request.profile_from_id,
        profile_to_id=request.profile_to_id,
        text=request.text
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@router.get('/{chat_id}')
async def read_messages(
        chat_id: int,
        current_user: src.schemas.UserCreate = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = get_profile(current_user, db)
    messages = db.query(models.Message).filter(
        and_(models.Message.chat_id == chat_id,
             models.Message.profile_to_id == profile.id)).all()
    for message in messages:
        message.viewed = True
        db.commit()
        db.refresh(message)
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    chat.check = True
    db.commit()
    db.refresh(chat)

    if profile.id == chat.profile_first_id:
        profile_id = chat.profile_second_id
    elif profile.id == chat.profile_second_id:
        profile_id = chat.profile_first_id

    read_chat = {
        'chat_id': chat.id,
        'type': '__read__'
    }

    await WSC.send_id_message(json.dumps(read_chat, ensure_ascii=False), profile_id)
    return 'messages is read'


@router.get('/update/{message_id}')
async def read_message(
        message_id: int,
        current_user: src.schemas.UserCreate = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = get_profile(current_user, db)
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    chat = db.query(models.Chat).filter(models.Chat.id == message.chat_id).first()
    message.viewed = True
    chat.check = True
    db.commit()
    db.refresh(message)
    db.refresh(chat)

    if profile.id == chat.profile_first_id:
        profile_id = chat.profile_second_id
    elif profile.id == chat.profile_second_id:
        profile_id = chat.profile_first_id

    read_chat = {
        'chat_id': chat.id,
        'type': '__read__'
    }

    await WSC.send_id_message(json.dumps(read_chat, ensure_ascii=False), profile_id)
    return message


@router.get('/audio/file')
def get_audio():
    return FileResponse('static/audio/message-audio.mp3')


@router.get('/get/{chat_id}')
def get_messages(chat_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    messages = \
        db.query(models.Message)\
            .filter(models.Message.chat_id == chat_id)\
            .order_by(models.Message.datetime_create.desc()) \
            .offset(skip).limit(limit).all()
    return messages


@router.patch('/{message_id}')
async def update_message(
        message_id: int,
        new_text: str,
        db: Session = Depends(get_db)
):
    updated_message = update_msg(message_id, new_text, db)
    await WSC.send_id_message(json.dumps(updated_message, ensure_ascii=False), updated_message['profile_to_id'])
    return 'message is updated'


@router.delete('/{message_id}')
async def delete_message(
        message_id: int,
        db: Session = Depends(get_db)
):
    deleted_message = delete_msg(message_id, db)
    await WSC.send_id_message(json.dumps(deleted_message, ensure_ascii=False), deleted_message['profile_to_id'])
    return 'message is deleted'


@router.get('/image/')
def get_image(type_file: str):
    if type_file == 'edit':
        return FileResponse('static/messages/edit-message.png')
    elif type_file == 'delete':
        return FileResponse('static/messages/delete-message.png')
