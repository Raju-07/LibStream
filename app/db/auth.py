# Dependencies imports
import uuid
import logging
from datetime import datetime,timezone,timedelta

#sqlalchemy & Fastapi imports
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException,status,APIRouter

#app imports
from app.models import UserModal
from .session import get_async_db
from app.schemas import UserRegister,UserResponse
from app.core.security import hash_password,create_session_token,verify_password

#Router
router = APIRouter(prefix='/auth',tags=["Authentication"])
# Defining auth logger
logger = logging.getLogger('app.auth')

now = datetime.now(timezone.utc) # current datetime 

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def create_user(
    user:UserRegister,
    db:AsyncSession = Depends(get_async_db)):
    logger.info("Registration request received for %s", user.username)

    try:
        existing_user = (await db.execute(
            select(UserModal).where(UserModal.username == user.username)
        )).scalar_one_or_none()
        logger.info(f'Checking if users username exists.')

        if existing_user:
            logger.warning(f'User already exists with that username')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists with that username"
            )

        existing_email = (await db.execute(
            select(UserModal).where(UserModal.email == user.email)
        )).scalar_one_or_none()
        logger.info(f"Checking if user's email exists.")

        if existing_email:
            logger.warning("User already exists with that Email.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already exists with that email."
            )
        logger.info("Hashing Password")
        hashed_password = hash_password(user.password)
        logger.info("Hashing Password complete.")

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
        logger.info("User registered successfully: %s", user.username)
        return new_user
    
    except HTTPException:
        raise

    except SQLAlchemyError as e:
        # CRITICAL: Database connection/query failure - application can't proceed
        logger.critical(f"Database error during registration for {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

    except Exception as e:
        logger.error(f"Unexpected error during registration for {user.username}: {str(e)}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error while creating user: {e}")


@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(UserModal).where(UserModal.username == form_data.username))
    user = user.scalar_one_or_none()
    if not user.is_active:
        logger.warning("Login rejected for banned user: %s", form_data.username)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "You're bann from using this application. Contact Admin 'admin123@libstream.com' for more information")
    
    if not user or not verify_password(form_data.password, user.password):
        logger.warning("Login failed for %s", form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    
    access_token = create_session_token(
        data={
            'sub':str(user.id),
            'iat':now,
            'jti':str(uuid.uuid4()),
            'type':'access'
            })
    logger.info(f"User: {form_data.username} login successfully.")
    return {'access_token':access_token,'token_type':'bearer'}