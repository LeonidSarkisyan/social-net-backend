from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, Form, File
from fastapi.responses import FileResponse
from passlib.context import CryptContext
import src.models as models
import src.schemas
from src.database import get_db
from sqlalchemy.orm import Session
from src.oauth2 import get_current_user
from src.utils.users import get_profile
from pydantic import BaseModel
from PIL import Image
import os
import uuid
from src.utils import posts


router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


@router.post('/', response_model=src.schemas.Post)
def create_post(post: src.schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(
        text=post.text,
        datetime_create=datetime.now(),
        profile_id=post.profile_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.post('/image')
def create_file_post(file: UploadFile = File(), post_id: int = Form(), db: Session = Depends(get_db)):
    with Image.open(file.file) as img:
        image = open(f'static/posts/{file.filename}', 'w')
        image.close()
        img.save(f'static/posts/{file.filename}')

    new_photo = models.ImagePost(url=file.filename, post_id=post_id)
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return FileResponse(f'static/posts/{file.filename}')


@router.get('/', response_model=list[src.schemas.Post])
def get_list_post(db: Session = Depends(get_db)):
    return db.query(models.Post).order_by(models.Post.datetime_create.desc()).all()


@router.get('/news', response_model=list[src.schemas.Post])
def get_news(skip: int = 0, limit: int = 3, db: Session = Depends(get_db)):
    news = db.query(models.Post).order_by(models.Post.datetime_create.desc()).offset(skip).limit(limit).all()
    return news


@router.get('/{profile_id}', response_model=list[src.schemas.Post])
def get_list_post_for_id(profile_id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post)\
        .filter(models.Post.profile_id == profile_id)\
        .order_by(models.Post.datetime_create.desc())\
        .all()
    return posts


@router.get('/one/{post_id}', response_model=src.schemas.Post)
def get_post_id(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    return post


@router.delete('/{post_id}')
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    for image in post.images:
        os.remove(f'static/posts/{image.url}')
    db.delete(post)
    db.commit()
    return 'post is deleted'


@router.get('/{post_id}/profile')
def get_profile_for_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    return post.profile


@router.get('/{post_id}/images')
def get_images_for_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    return post.images


@router.get('/images/{image_id}')
def get_image_post(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.ImagePost).filter(models.ImagePost.id == image_id).first()
    return FileResponse(f'static/posts/{image.url}')


@router.post('/images/{post_id}')
def upload_multiple_files(post_id: int, files: list[UploadFile] = File(), db: Session = Depends(get_db)):
    for file in files:
        name = str(uuid.uuid4().hex)
        filename, ext = os.path.splitext(file.filename)
        with Image.open(file.file) as img:
            image = open(f'static/posts/{name + ext}', 'w')
            image.close()
            img.save(f'static/posts/{name + ext}')
        new_photo = models.ImagePost(url=name + ext, post_id=post_id)
        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)
    return 'good'


@router.put('/{post_id}')
def update_post(post_id: int, updated_text: str, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    post.text = updated_text
    db.commit()
    db.refresh(post)
    return updated_text























