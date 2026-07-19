#dependency imports
import uuid

#Fastapi & slqalchemy 
from fastapi import Depends,status,HTTPException,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_,and_,select,func,insert

#app imports
from app.db.session import get_async_db
from app.models import BooksModal,UserModal,BookAssignModal
from app.schemas import BookRequest,BookAssignRequest, UserResponse,ViewBookResponse
from app.api.dependencies import get_current_user



router = APIRouter(prefix="/books",tags=["Book Operations"])

@router.get("/search-by-name")
async def get_book_by_name(bookname: str,
                        category:str = 'all' ,
                        db:AsyncSession = Depends(get_async_db)):
    query = select(BooksModal).where(BooksModal.name.ilike(f'%{bookname}%'))
    
    if category != 'all':
        query = query.where(BooksModal.category.ilike(f'%{category}%'))

    result = await db.execute(query)
    books = result.scalars().all()

    if not len(books) > 0:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail=f"Nothing Found with Name {bookname}")
    return books

@router.get("/search-by-id/{id}",response_model=ViewBookResponse)
async def get_book_by_id(id:int, db: AsyncSession = Depends(get_async_db)):
    conditions = [BooksModal.id == id]
    count_result = await db.execute(
        select(func.count(BooksModal.id)).where(*conditions))
    count = count_result.scalar()

    if count == 0:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"No Book Found with {id= }"
        )
    results = await db.execute(select(BooksModal).where(and_(*conditions)))
    books = results.scalar_one_or_none()

    return books


@router.get('/available-books')
async def get_avail_books(db: AsyncSession = Depends(get_async_db)):
    condition = [BooksModal.is_assigned == False]
    query = await db.execute(select(func.count(BooksModal.id)).where(and_(*condition)))
    count = query.scalar()

    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There isn't any book available yet"
        )
    
    books = await db.execute(select(BooksModal).where(and_(*condition)))
    return books.scalars().all()






