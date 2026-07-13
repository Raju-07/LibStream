import uuid

from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
import jwt
from app.models import UserModal
from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


oauth_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth_schema),
                    db: AsyncSession = Depends(get_async_db)) -> UserModal:
    
    credential_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail='could not validate credential',
        headers={"WWW-AUTHENTICATE":"bearer"}
    )
    try:
        payload = jwt.decode(token,settings.secret_key,settings.algorithm)
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Token has Expired")
    
    except jwt.PyJWTError:
        raise credential_exception
    
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        raise credential_exception

    result = await db.execute(
        select(UserModal).where(
            UserModal.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credential_exception
    
    return user


async def admin_required(
        current_user : UserModal = Depends(get_current_user)) -> None:
    if not current_user.is_admin:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Admin Privileges Required")
    

async def get_admin_user(
        current_user: UserModal= Depends(get_current_user)) -> UserModal:
    if not current_user.is_admin:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Admin Privileges Required")
    return current_user
    