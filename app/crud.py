from app.api.dependencies import admin_required,is_book_exists
from sqlalchemy import select,and_,delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,APIRouter,HTTPException,status
from app.schemas import AddBookRequest,UpdateBookRequest
from app.db.session import get_async_db
from app.models import BooksModal
from app.db.books_user_operation import get_book_by_id

router = APIRouter(prefix='/admin',tags=["Admin Operations"])

@router.post('/add-book')
async def add_book(
    book:AddBookRequest,
    _ : None = Depends(admin_required),
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
                            _: None = Depends(admin_required)):
    
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
    

@router.patch("/update-book/{id}",status_code=status.HTTP_200_OK)
async def update_book(book: UpdateBookRequest ,id: int = Depends(is_book_exists),
                       db: AsyncSession = Depends(get_async_db),
                       _:None = Depends(admin_required)):
    # updating book
    try:
        result = await db.execute(select(BooksModal).where(BooksModal.id == id))
        exists_book = result.scalar_one_or_none()

        #unpacking all the data to it's column
        data_update = book.model_dump(exclude_unset=True)
        for key, values in data_update.items():
            setattr(exists_book,key,values)

        await db.commit()
        await db.refresh(exists_book)

        return {
            'code':200,
            'message':"Book has been updated.",
            'updated book': exists_book
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error while updating Book : {str(e)}")