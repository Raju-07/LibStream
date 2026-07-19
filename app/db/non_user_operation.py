#dependency imports
import uuid
from typing import Optional

#Fastapi & slqalchemy 
from fastapi import Depends, Query,status,HTTPException,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_,and_,select,func,insert

#app imports
from app.db.session import get_async_db
from app.models import BooksModal,UserModal,BookAssignModal
from app.schemas import BookRequest,BookAssignRequest, UserResponse,ViewBookResponse
from app.models import BookCategory



router = APIRouter(prefix="/books",tags=["Book Operations"])

@router.get("/search-by-name",response_model=list[ViewBookResponse])
async def get_book_by_name(
    bookname: str = Query(..., min_length=1, description="Book name to search for"),
    category: Optional[BookCategory] = Query(None, description="Filter by category (optional)"),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        # Build base query with name search
        query = select(BooksModal).where(BooksModal.name.ilike(f'%{bookname}%'))
        
        # Add category filter if specified
        if category is not None:
            query = query.where(BooksModal.category == category)
                
        result = await db.execute(query)
        books = result.scalars().all()
        
        # Check if any books found
        if not books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No books found with name '{bookname}'"
            )
        return books
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while searching for books: {e}"
        )

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






