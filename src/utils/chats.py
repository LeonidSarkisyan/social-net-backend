from datetime import datetime
from src.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import src.models as models
import src.schemas
from fastapi import Depends


def is_chat_exist(chat: src.schemas.ChatCreate, db: Session):
    chat = db.query(models.Chat).filter(
        or_(
           and_(
               models.Chat.profile_first_id == chat.profile_first_id,
               models.Chat.profile_second_id == chat.profile_second_id
           ),
           and_(
               models.Chat.profile_first_id == chat.profile_second_id,
               models.Chat.profile_second_id == chat.profile_first_id
           )
        )
    ).first()
    return chat


def create_chat(chat: src.schemas.ChatCreate, db: Session):
    new_chat = models.Chat(
        profile_first_id=chat.profile_first_id,
        profile_second_id=chat.profile_second_id,
        datetime_create=datetime.now()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat
