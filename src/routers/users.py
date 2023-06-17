from fastapi import APIRouter, Depends
from passlib.context import CryptContext
import src.models as models
import src.schemas
from src.database import get_db
from sqlalchemy.orm import Session
from src.hashing import Hash
from src.oauth2 import get_current_user
from src.utils.users import get_profile

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/', response_model=src.schemas.UserAfterCreate)
def create_user(user: src.schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(
        username=user.username,
        password=Hash.bcrypt(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(new_user.__dict__)
    return new_user


@router.get('/me')
def private(current_user: src.schemas.UserCreate = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_profile(current_user, db)

