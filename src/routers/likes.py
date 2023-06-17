from datetime import datetime
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
import src.models as models
import src.schemas
from src.database import get_db
from sqlalchemy.orm import Session
from src.oauth2 import get_current_user
from src.utils.users import get_profile
from fastapi.responses import FileResponse

router = APIRouter(
    prefix='/likes',
    tags=['likes']
)


@router.get('/full')
def get_full_like():
    return FileResponse('static/utils/like-full.png')


@router.get('/unfull')
def get_unfull_like():
    return FileResponse('static/utils/like-unfull.png')


@router.post('/')
def create_like(like: src.schemas.Like, db: Session = Depends(get_db)):
    new_like = models.Like(post_id=like.post_id, user_id=like.user_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like


@router.delete('/{like_id}/')
def delete_like(like_id: int, db: Session = Depends(get_db)):
    like = db.get(models.Like, like_id)
    db.delete(like)
    db.commit()
    return 'like deleted'


@router.get('/{post_id}/count/')
def get_count_likes_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    count_likes = post.likes
    return count_likes











