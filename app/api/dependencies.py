from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
import jwt


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

async def current_user_admin(token: str = Depends(oauth_schema)):
    payload = jwt.decode(token,settings.secret_key,settings.algorithm)
    admin = payload.get('admin')
    if admin:
        return {'code':'','message':"you're elegible to perform this operation"}
    else:
        return {'code':'401','message':'Unauthorized Action'}
