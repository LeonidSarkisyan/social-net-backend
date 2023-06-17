import this

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from PIL import Image
from sqlalchemy.orm import Session
from src.oauth2 import get_current_user
from src.database import get_db
from src.utils.users import get_profile
from sqlalchemy import and_, or_
from src.utils import group as group_utils
import sqlalchemy
import src.models as models
import src.schemas
import uuid
import os


router = APIRouter(
    prefix='/groups',
    tags=['groups']
)


@router.post('/')
def create_group(
        group: src.schemas.GroupCreate,
        user: src.schemas.UserCreate = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = get_profile(user, db)
    try:
        new_group = models.Group(
            title=group.title, genre=group.genre, count_subscribers=0, creator_id=profile.id, tag_name=group.tag_name
        )
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group
    except Exception:
        raise HTTPException(status_code=403, detail='Such already exists')


@router.get('/page/{tag_name}')
def get_group(tag_name: str, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.tag_name == tag_name).first()
    return group


@router.get('/')
def get_group_list(db: Session = Depends(get_db)):
    groups = db.query(models.Group).all()
    return groups


@router.get('/my')
def get_my_group_list(user: src.schemas.UserCreate = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_profile(user, db)
    groups = db.query(models.Group).filter(models.Group.creator_id == profile.id).all()
    return groups


@router.post('/avatar')
def upload_avatar_group(
  file: UploadFile = File(),
  group_id: int = Form(),
  user: src.schemas.UserCreate = Depends(get_current_user),
  db: Session = Depends(get_db)
):
    name = str(uuid.uuid4().hex)
    filename, ext = os.path.splitext(file.filename)
    print(file.filename)
    with Image.open(file.file) as img:
        image = open(f'static/groups/{name + ext}', 'w')
        image.close()
        img.save(f'static/groups/{name + ext}')
    new_photo = models.GroupAvatar(url=name + ext, group_id=group_id)
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return 'good'


@router.get('/avatar/{group_id}')
def get_group_avatar(group_id: int, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    try:
        avatar = group.avatar[0]
    except IndexError:
        avatar = None

    if avatar:
        return FileResponse(f'static/groups/{avatar.url}')
    else:
        return FileResponse(f'static/utils/not-avatar.png')


@router.get('/subscribed/{profile_id}', response_model=list[src.schemas.SubGroup])
def get_subscribed_groups(
        profile_id: int,
        user: src.schemas.UserCreate = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subs = db.query(models.Subscriber).filter(models.Subscriber.profile_id == profile_id).all()
    return subs


# API-методы с подписчиками

@router.get('/subscribe/{group_id}')
def subscribe_group(
        group_id: int, db: Session = Depends(get_db),
        user: src.schemas.UserCreate = Depends(get_current_user)
):
    profile = get_profile(user, db)
    new_sub = models.Subscriber(profile_id=profile.id, group_id=group_id)
    group_utils.new_sub_count_plus(group_id, db)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return 'new sub'


@router.delete('/subscribe/{group_id}')
def un_subscribe_group(
        group_id: int, db: Session = Depends(get_db),
        user: src.schemas.UserCreate = Depends(get_current_user)
):
    profile = get_profile(user, db)
    sub = db.query(models.Subscriber).filter(
        and_(
             models.Subscriber.group_id == group_id,
             models.Subscriber.profile_id == profile.id
        )
    ).first()
    group_utils.new_sub_count_minus(group_id, db)
    db.delete(sub)
    db.commit()
    return 'you un sub'


@router.get('/subscribe/all/{group_id}')
def get_subscribers_list(group_id: int, db: Session = Depends(get_db)):
    subs = db.query(models.Group).filter(models.Group.id == group_id).first().subscribers
    return subs
