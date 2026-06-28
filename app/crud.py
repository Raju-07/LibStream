from fastapi import Depends,status,HTTPException,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_
from app.db.session import get_db
from app.models import BooksModal
router = APIRouter(prefix="/books",tags=["Book Operations"])


@router.get("/search")
async def get_book_by_name(bookname: str,category: str='all',db: Session = Depends(get_db)):
    book = db.query(BooksModal).filter(BooksModal.name.ilike(f'%{bookname}%')).all()
    return book





