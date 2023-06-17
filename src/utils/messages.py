import datetime
import time
import src.schemas
import src.models as models
from sqlalchemy.orm import Session


def create_message(data: dict, profile_id: int, db: Session):

    datetime_create = time.mktime(datetime.datetime.now().timetuple())

    new_message = models.Message(
        text=data['text'],
        profile_from_id=profile_id,
        profile_to_id=data['profile_to_id'],
        chat_id=data['chat_id'],
        datetime_create=datetime.datetime.now(),
        datetime_update=datetime.datetime.now(),
        datetime_create_float=datetime_create,
        datetime_update_float=datetime_create
    )

    chat = db.query(models.Chat).filter(models.Chat.id == data['chat_id']).first()
    chat.check = False
    chat.datetime_create = datetime.datetime.now()

    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    db.refresh(chat)

    message = {
        'id': new_message.id,
        'viewed': new_message.viewed,
        'text': new_message.text,
        'datetime_create_float': new_message.datetime_create_float,
        'datetime_update_float': new_message.datetime_update_float,
        'profile_from_id': new_message.profile_from_id,
        'profile_to_id': new_message.profile_to_id,
        'chat_id': new_message.chat_id
    }
    return message


def update_message(message_id: int, new_text: str, db: Session):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    message.text = new_text
    message.datetime_update = datetime.datetime.now()
    message.datetime_update_float = time.mktime(datetime.datetime.now().timetuple())
    db.commit()
    db.refresh(message)

    updated_message = {
        "id": message.id,
        "text": message.text,
        "profile_from_id": message.profile_from_id,
        "profile_to_id": message.profile_to_id,
        "viewed": message.viewed,
        "chat_id": message.chat_id,
        "datetime_create_float": message.datetime_create_float,
        "datetime_update_float": message.datetime_update_float,
        "type": '__update__'
    }
    return updated_message


def delete_message(message_id: int, db: Session):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    db.delete(message)
    db.commit()

    deleted_message = {
        "id": message.id,
        "chat_id": message.chat_id,
        "profile_to_id": message.profile_to_id,
        "type": '__delete__',
    }
    return deleted_message

