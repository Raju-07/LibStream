from fastapi import Depends,status,HTTPException,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_
from app.db.session import get_db
from app.models import BooksModal
router = APIRouter(prefix="/books",tags=["Book Operations"])


@router.get("/search-by-name")
async def get_book_by_name(bookname: str, category:str = 'all' ,db: Session = Depends(get_db)):
    result = db.query(BooksModal).filter(BooksModal.name.ilike(f'%{bookname}%')).all()
    
    if category != 'all':
        result = db.query(BooksModal).filter(
            and_(BooksModal.name.ilike(f'%{bookname}%'),
                 BooksModal.category == category)).all()

    # if not len(result) > 0:
    #     raise HTTPException(status_code = status.HTTP_200_OK,
    #                         detail="Nothing Found 404")
    return result

@router.get("/search-by-id")
async def get_book_by_id(id:int,db:Session = Depends(get_db)):
    result = db.query(BooksModal).filter(BooksModal.id == id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book Not Found with {id=} ")
    else:
        if result.is_assigned == True:        
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_306_RESERVED,
                detail="Book is already in used")

