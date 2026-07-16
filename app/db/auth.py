from .session import get_async_db
from fastapi import Depends,HTTPException,status,APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import UserRegister,UserResponse
from app.models import UserModal
from app.core.security import hash_password,create_session_token,verify_password
import uuid
from datetime import datetime,timezone,timedelta

router = APIRouter(prefix='/auth',tags=["Authentication"])
# current datetime 
now = datetime.now(timezone.utc)

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def createuser(
    user:UserRegister,
    db:AsyncSession = Depends(get_async_db)):

    existing_user = (await db.execute(
        select(UserModal).where(UserModal.username == user.username)
    )).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with that username"
        )

    existing_email = (await db.execute(
        select(UserModal).where(UserModal.email == user.email)
    )).scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already exists with that email."
        )

    hashed_password = hash_password(user.password)
    new_user = UserModal(
        id=uuid.uuid4(),
        name=user.name,
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(UserModal).where(UserModal.username == form_data.username))
    user = user.scalar_one_or_none()
    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "You're bann from using this application. Contact Admin 'admin123@libstream.com' for more information")
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    
    access_token = create_session_token(
        data={
            'sub':str(user.id),
            'iat':now,
            'jti':str(uuid.uuid4()),
            'type':'access'
            })
    return {'access_token':access_token,'token_type':'bearer'}