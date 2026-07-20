#dependency imports
import logging
from typing import Optional

#Fastapi & slqalchemy 
from fastapi import Depends, Query,status,HTTPException,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_,and_,select,func,insert

#app imports
from app.db.session import get_async_db
from app.models import BooksModal
from app.schemas import  ViewBookResponse
from app.models import BookCategory



router = APIRouter(prefix="/books",tags=["Book Operations"])
logger = logging.getLogger("app")
db_logger = logging.getLogger("app.datababse")

@router.get("/search",response_model=list[ViewBookResponse])
async def search_books(
    bookname: str = Query(..., min_length=1, description="Book name to search for"),
    category: Optional[BookCategory] = Query(None, description="Filter by category (optional)"),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        logger.info("Book search requested for %s", bookname)
        db_logger.info("Executing book search query")
        query = select(BooksModal).where(BooksModal.name.ilike(f'%{bookname}%'))
        
        # Add category filter if specified
        if category is not None:
            query = query.where(BooksModal.category == category)
                
        result = await db.execute(query)
        books = result.scalars().all()
        
        # Check if any books found
        if not books:
            logger.warning("No books found for search term: %s", bookname)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No books found with name '{bookname}'"
            )
        logger.info("Book search returned %s result(s)", len(books))
        return books
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while searching for books: {e}"
        )

@router.get("/{book_id}",response_model=ViewBookResponse)
async def get_book_by_id(book_id:int, db: AsyncSession = Depends(get_async_db)):
    db_logger.info("Fetching book by id: %s", book_id)
    conditions = [BooksModal.id == book_id]
    count_result = await db.execute(
        select(func.count(BooksModal.id)).where(*conditions))
    count = count_result.scalar()

    if count == 0:
        logger.warning("Book not found with id: %s", book_id)
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"No Book Found with {book_id = }"
        )
    results = await db.execute(select(BooksModal).where(and_(*conditions)))
    books = results.scalar_one_or_none()
    logger.info("Book fetched successfully: %s", book_id)

    return books


@router.get('/available')
async def get_available_books(db: AsyncSession = Depends(get_async_db)):
    logger.info("Available books request received")
    condition = [BooksModal.is_assigned == False]
    query = await db.execute(select(func.count(BooksModal.id)).where(*condition))
    count = query.scalar()

    if count == 0:
        logger.info("No available books found")
        return {
            'code':404,
            'message': "There isn't any book available yet",
                }

    books = await db.execute(select(BooksModal).where(and_(*condition)))
    logger.info("Available books returned: %s", count)
    return books.scalars().all()
