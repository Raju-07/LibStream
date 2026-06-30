from fastapi import Depends,status,HTTPException,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_
from app.db.session import get_db
from app.models import BooksModal,UserModal,BookAssignModal
from app.schemas import BookResponse
from app.api.dependencies import get_current_user


router = APIRouter(prefix="/books",tags=["Book Operations"])

@router.get("/search-by-name")
async def get_book_by_name(bookname: str, category:str = 'all' ,db: Session = Depends(get_db)):
    result = db.query(BooksModal).filter(BooksModal.name.ilike(f'%{bookname}%')).all()
    
    if category != 'all':
        result = db.query(BooksModal).filter(
            and_(BooksModal.name.ilike(f'%{bookname}%'),
                 BooksModal.category == category)).all()

    if not len(result) > 0:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail=f"Nothing Found with Name {bookname}")
    return result

@router.get("/search-by-id",response_model=BookResponse)
async def get_book_by_id(id:int,db:Session = Depends(get_db)):
    result = db.query(BooksModal).filter(BooksModal.id == id)
    if not result.count() > 0:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail='Not Found 404')
    return result.first()

@router.patch("/take-book/{id}")
async def take_book(id: int,current_user: UserModal= Depends(get_current_user),
                   db: Session = Depends(get_db)):
    
    book = db.query(BooksModal).filter(
        and_(BooksModal.id == id,BooksModal.is_assigned == False)).first()
    
    if  not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Book isn't available")
    
    book_assigned = BookAssignModal(
        user_id = current_user.id,
        book_id = book.id,

    )
    
    return book

