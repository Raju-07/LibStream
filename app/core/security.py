import bcrypt
import jwt

from datetime import datetime,timedelta,timezone
from app.core.config import settings

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

