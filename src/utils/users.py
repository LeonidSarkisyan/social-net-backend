import src.models as models
import src.schemas
from sqlalchemy.orm import Session


def get_profile(username: str, db: Session) -> src.schemas.ProfileComment:
    return db.query(models.User).filter(models.User.username == username).first().profile[0]
