from app.api.dependencies import get_admin_user,admin_required
from sqlalchemy import select,and_,delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,APIRouter,HTTPException,status
from app.schemas import BookRequest,BookResponse
from app.db.session import get_async_db
from app.models import BooksModal

router = APIRouter(prefix='/admin',tags=["Admin Operations"])

@router.post('/add-book')
async def add_book(
    book:BookRequest,
    admin_user : AsyncSession = Depends(admin_required),
    db: AsyncSession = Depends(get_async_db)
    ):
    try:
        new_book = BooksModal(**book.model_dump())
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)
    except:
        await db.rollback()
    return new_book


@router.delete("/delete-book/{id}")
async def delete_book_by_id(id:int,
                            db: AsyncSession = Depends(get_async_db),
                            admin: AsyncSession = Depends(admin_required)):
    
    try:
        await db.execute(delete(BooksModal).where(BooksModal.id == id))
        await db.commit()
        return {'code':200,
                'Message':"Book Deleted Successfully"}
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deletation Failed due to {e}"
        )