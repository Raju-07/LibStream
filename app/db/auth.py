from .session import get_db
from fastapi import Depends,HTTPException,status,APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import UserRegister,UserResponse
from app.models import UserModal
from app.core.security import hash_password,create_session_token,verify_password
import uuid

router = APIRouter(prefix='/auth',tags=["Authentication"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def createuser(user:UserRegister,db:Session = Depends(get_db)):
    username = db.query(UserModal).filter(UserModal.username == user.username).first()
    if username:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exists with that username")
    
    useremail = db.query(UserModal).filter(UserModal.email == user.email).first()
    if useremail:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Account already exists with that email.")
    
    hashed_password = hash_password(user.password)
    id = uuid.uuid4()
    new_user = UserModal(
        id = id,
        name=user.name,
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModal).filter(UserModal.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    
    access_token = create_session_token(data={'username':user.username,'admin':user.is_admin,"id":str(user.id),'email':user.email,'active':user.is_active})
    return {'access_token':access_token,'token_type':'bearer'}