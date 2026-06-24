from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
import bcrypt
import jwt
from datetime import datetime,timedelta,timezone
from .config import settings
from app.db.session import get_db
from app.models import UserModal

def hash_password(password: str) -> str:
    plain_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plain_bytes,salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes,hashed_bytes)
    except Exception:
        return False
    
def create_session_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = settings.token_expire_minutes)
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode,settings.secret_key,settings.algorithm)

def is_admin(user_id,db: Session = Depends(get_db))->bool:
    admin = db.query(UserModal).filter(UserModal.id == user_id).first()
    if admin:
        return True
    else:
        return False
