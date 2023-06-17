from fastapi import APIRouter, Depends, HTTPException
import src.models as models
import src.schemas
from src.database import get_db
from src.schemas import Login
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.hashing import Hash
from src.JWToken import create_access_token
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    tags=['authetication'],
    prefix='/authetication'
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post('/login')
def login(request: Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail='User does not exist')
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=403, detail='Incorrect password')

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

