from sqlalchemy.orm import Session
import src.models as models
import os


def delete_post(post_id: int, db: Session):
    db.query(models.Post).filter(models.Post.id == post_id).delete()
    images = db.query(models.ImagePost).filter(models.ImagePost.post_id == post_id)
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id)
    likes = db.query(models.Like).filter(models.Like.post_id == post_id)
    notifications = db.query(models.Notification).filter(models.Notification.comment.post.id == post_id)
    for image in images:
        os.remove(f'static/posts/{image.url}')
    images.delete()
    comments.delete()
    likes.delete()
    notifications.delete()
    db.commit()
    print('Работает всё')
    return 'post deleted'
