from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlmodel import select

from app.auth import create_access_token
from app.db import SessionDep
from app.models.user import User
from app.settings import settings

router = APIRouter(prefix="/api/auth")
password_hash = PasswordHash.recommended()


@router.post("/token")
def login(session: SessionDep, form: OAuth2PasswordRequestForm = Depends()):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if user is None or not password_hash.verify(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, settings.jwt_secret_key.get_secret_value())
    return {"access_token": token, "token_type": "bearer"}
