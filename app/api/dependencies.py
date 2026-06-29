from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
import jwt
from app.models import UserModal


oauth_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth_schema)) -> str:
    credential_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail='could not validate credential',
        headers={"WWW-AUTHENTICATE":"bearer"}
    )

    try:
        payload = jwt.decode(token,settings.secret_key,settings.algorithm)
        username = payload.get("username")
        if username is None:
            raise credential_exception
    except jwt.PyJWTError:
        raise credential_exception
    
    return username

async def get_admin_user(current_user: UserModal = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin user can perform this operation")
    return current_user