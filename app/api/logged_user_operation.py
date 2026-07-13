from fastapi import HTTPException,status,APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,and_,or_
from app.db.session import get_async_db
from app.api.dependencies import get_current_user
from app.models import BookAssignModal,UserModal


router = APIRouter(prefix='/user',tags=["Users Operation"])


@router.get("/my-books")
async def get_my_books(
    user: AsyncSession = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)):

    stmt = select(BookAssignModal).where(BookAssignModal.user_id == user)
    results = await db.execute(stmt)
    my_books = results.scalars().all()

    if my_books.count == 0:
        return {
            'code': 200,
            'message': "No books found"
        }
    
    return my_books
    
    
    