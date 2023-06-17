from fastapi import APIRouter, Depends, UploadFile, Form, File
from fastapi.responses import FileResponse

import src.schemas
from src.schemas import *
from sqlalchemy.orm import Session
import src.models as models
import shutil
import os
from PIL import Image
from src.oauth2 import get_current_user
from src.utils.users import get_profile

router = APIRouter(
    tags=['profiles'],
    prefix='/profile'
)


@router.post('/')
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    new_profile = models.Profile(tag_name=profile.tag_name, name=profile.name, surname=profile.surname, status=profile.status, city=profile.city,
                                 user_id=profile.user_id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.get('/{tagName}')
def get_profile_(tagName: str, db: Session = Depends(get_db), current_user: UserCreate = Depends(get_current_user)):
    profile = db.query(models.Profile).filter(models.Profile.tag_name == tagName).first()
    return profile


@router.get('/{id}')
def get_profile_id(id: int, db: Session = Depends(get_db)):
    profile = db.get(models.Profile, id)
    return profile


@router.get('/id/{id}')
def get_profile_id(id: int, db: Session = Depends(get_db)):
    profile = db.get(models.Profile, id)
    return profile


@router.get('/')
def list_profiles(db: Session = Depends(get_db)):
    profiles = db.query(models.Profile).all()
    return profiles


@router.post('/avatar')
def create_upload_file(file: UploadFile = File(), id: int = Form(), db: Session = Depends(get_db)):
    with Image.open(file.file) as img:
        image = open(f'static/avatars/{file.filename}', 'w')
        img.save(f'static/avatars/{file.filename}')
        image.close()
    new_photo = models.Photo(url=file.filename, user_id=id)
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return FileResponse(f'static/avatars/{new_photo.url}')


@router.post('/avatar/change')
def update_avatar_profile(
        file: UploadFile = Form(),
        user: UserCreate = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = get_profile(user, db)
    photo = db.query(models.Photo).filter(models.Photo.user_id == profile.id).first()

    with Image.open(file.file) as img:
        image = open(f'static/avatars/{file.filename}', 'w')
        img.save(f'static/avatars/{file.filename}')
        image.close()

    if photo:
        photo.url = file.filename
        db.commit()
        db.refresh(photo)
    else:
        new_photo = models.Photo(user_id=profile.id, url=file.filename)
        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)
    return 'all good!'



@router.get('/avatar/{profile_id}')
def get_file(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.tag_name == profile_id).first()
    try:
        file_name = profile.photos[0].url
    except IndexError:
        return FileResponse(f'static/utils/not-avatar.png')
    return FileResponse(f'static/avatars/{file_name}')


@router.get('/avatar/v2/{profile_id}')
def get_file_v2(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    try:
        file_name = profile.photos[0].url
    except IndexError:
        return FileResponse(f'static/utils/not-avatar.png')
    return FileResponse(f'static/avatars/{file_name}')


@router.get('/avatar/not/authetication')
def get_none_avatar():
    return FileResponse('static/utils/login.png')


@router.get('/like/no')
def get_no_like():
    return FileResponse('static/utils/like-unfull.png')


@router.get('/like/yes')
def get_yes_like():
    return FileResponse('static/utils/like-full.png')


@router.patch('/{profile_id}')
def update_profile(profile_id: int, update_body: src.schemas.UpdateProfile, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    profile.name = update_body.name if update_body.name is not None else profile.name
    profile.surname = update_body.surname if update_body.surname is not None else profile.surname
    profile.status = update_body.status if update_body.status is not None else profile.status
    profile.city = update_body.city if update_body.city is not None else profile.city
    profile.tag_name = update_body.tag_name if update_body.tag_name is not None else profile.tag_name
    db.commit()
    db.refresh(profile)
    return profile

