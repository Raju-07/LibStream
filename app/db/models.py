from .session import get_db
from fastapi import Depends,HTTPException,status,APIRouter
from sqlalchemy.orm import Session
from schemas import UserRegister,UserResponse
from ..models import UserModal
from ..core.security import hash_password

router = APIRouter(prefix='/auth',tags=["Authentication"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def createuser(user:UserRegister,db:Session = Depends(get_db)):
    username = db.query(UserModal).filter(UserModal.username == user.username).first()
    if username:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exists with that username")
    
    useremail = db.query(UserModal).filter(UserModal.email == user.email).first()
    if useremail:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Account already exists with that email.")
    
    hashed_password = hash_password(user.password)

    new_user = UserModal(
        name = user.name,
        username = user.username,
        email = user.email,
        password = hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

