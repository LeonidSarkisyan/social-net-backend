from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.JWToken import verify_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authetication/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)
