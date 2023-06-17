import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, status
import src.models as models
import src.schemas
from src.database import get_db

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import src.notifications


router = APIRouter(
    prefix='/requestsfriends',
    tags=['requestsfriends']
)


@router.get('/{profile_id}')
def get_list_request(profile_id: int, db: Session = Depends(get_db)):
    requests = db.query(models.RequestFriend).filter(models.RequestFriend.profile_from_id == profile_id).all()
    return requests


@router.post('/')
async def create_requestfriend(request: src.schemas.RequestFriendCreate, db: Session = Depends(get_db)):
    new_request = models.RequestFriend(
        profile_from_id=request.profile_from_id,
        profile_to_id=request.profile_to_id,
        date=datetime.datetime.now()
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    noti = notifications.create_notification_request_friend(new_request, db)
    noti = json.dumps(noti, ensure_ascii=False)
    await notifications.wrire_message_id(noti, new_request.profile_to_id)
    return new_request


@router.post('/{request_id}/accept')
async def accept_request(request_id: int, db: Session = Depends(get_db)):
    request = db.get(models.RequestFriend, request_id)
    if request.accept == True:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Запрос уже был принят')
    request.accept = True
    new_accept_friend = models.AcceptFriend(
        who_accept_id=request.profile_to_id,
        who_send_id=request.profile_from_id,
        date=datetime.datetime.now(),
        request_friend_id=request.id
    )
    new_friend1 = models.Friend(
        profile_id=new_accept_friend.who_send_id,
        friend_id=new_accept_friend.who_accept_id
    )
    new_friend2 = models.Friend(
        profile_id=new_accept_friend.who_accept_id,
        friend_id=new_accept_friend.who_send_id
    )

    chat = db.query(models.Chat).filter(
        or_(
            and_(
                models.Chat.profile_first_id == new_accept_friend.who_accept_id,
                models.Chat.profile_second_id == new_accept_friend.who_send_id
            ),
            and_(
                models.Chat.profile_first_id == new_accept_friend.who_send_id,
                models.Chat.profile_second_id == new_accept_friend.who_accept_id
            )
        )
    ).first()

    if not chat:
        new_chat = models.Chat(
            profile_first_id=new_accept_friend.who_send_id,
            profile_second_id=new_accept_friend.who_accept_id,
            datetime_create=datetime.datetime.now()
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

    db.add(new_accept_friend)
    db.bulk_save_objects((new_friend1, new_friend2))
    db.commit()
    db.refresh(request)
    db.refresh(new_accept_friend)


    noti = notifications.create_notification_accept_friend(new_accept_friend, db)
    noti = json.dumps(noti, ensure_ascii=False)
    await notifications.wrire_message_id(noti, new_accept_friend.who_send_id)
    return request


@router.delete('/{request_id}')
def delete_request(request_id: int, db: Session = Depends(get_db)):
    request = db.get(models.RequestFriend, request_id)
    if request:
        db.delete(request)
        db.commit()
        return 'request id deleted'
    else:
        raise HTTPException(status_code=404, detail='Такого запроса не существует')


