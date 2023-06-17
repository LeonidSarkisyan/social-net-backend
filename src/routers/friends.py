import sqlalchemy
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.oauth2 import get_current_user
from src.database import get_db
from src.utils.users import get_profile
from sqlalchemy import and_, or_
import src.models as models
import src.schemas

router = APIRouter(
    prefix='/friend',
    tags=['friend']
)


@router.get('/{profile_id}', response_model=list[src.schemas.FriendOut])
def get_friend_list(profile_id: int, db: Session = Depends(get_db)):
    friends = db.query(models.Friend).filter(models.Friend.profile_id == profile_id).all()
    return friends


@router.get('/{profile_id}/limit/')
def get_friend_list_with_limit(profile_id: int, limit: int = None, db: Session = Depends(get_db)):
    if limit:
        friends = db.query(models.Friend).filter(models.Friend.profile_id == profile_id).limit(limit).all()
    else:
        friends = db.query(models.Friend).filter(models.Friend.profile_id == profile_id).all()
    return friends


@router.get('/profile/{profile_id}')
def get_profile_friend_id(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(models.Profile, profile_id)
    return profile


@router.delete('/delete/{friend_id}')
def delete_friend(
        friend_id: int,
        db: Session = Depends(get_db),
        current_user: src.schemas.UserCreate = Depends(get_current_user)
):
    current_profile = get_profile(current_user, db)
    db.query(models.Friend).filter(
        or_(
            and_(models.Friend.profile_id == current_profile.id, models.Friend.friend_id == friend_id),
            and_(models.Friend.profile_id == friend_id, models.Friend.friend_id == current_profile.id)
        )
    ).delete()

    request_friend = db.query(models.RequestFriend).filter(
        or_(
            and_(
                models.RequestFriend.profile_from_id == current_profile.id,
                models.RequestFriend.profile_to_id == friend_id
            ),
            and_(
                models.RequestFriend.profile_from_id == friend_id,
                models.RequestFriend.profile_to_id == current_profile.id
                )
        )
    ).first()

    if request_friend.profile_from_id == current_profile.id:
        db.delete(request_friend)
        db.commit()
        return 'friend is deleted'
    else:
        request_friend.accept = False
        db.commit()
        db.refresh(request_friend)
        return request_friend
