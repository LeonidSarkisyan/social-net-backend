import src.models as models
import src.schemas
from sqlalchemy.orm import Session


def new_sub_count_plus(group_id: int, db: Session):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    group.count_subscribers += 1
    db.commit()
    db.refresh(group)
    return group


def new_sub_count_minus(group_id: int, db: Session):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    group.count_subscribers -= 1
    db.commit()
    db.refresh(group)
    return group
