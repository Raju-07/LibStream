from app.api.dependencies import admin_required,is_book_exists
from sqlalchemy import select,and_,delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,APIRouter,HTTPException,status
from app.schemas import AddBookRequest,UpdateBookRequest
from app.db.session import get_async_db
from app.models import BooksModal,UserModal
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
async def delete_book_by_id(id:int = Depends(get_book_by_id),
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
    
    

# Endpoint to ban User's
@router.patch("/ban-user/{username}")
async def ban_user(username: str,_ : None = Depends(admin_required),
                   db: AsyncSession = Depends(get_async_db)):
    try:
        user = await db.execute(select(UserModal).where(UserModal.username == username))
        user = user.scalar_one_or_none()

        if not user.is_active:
            return {
                'code':200,
                'message': "user is already Banned."
            }

        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                f"{username} doesn't exists")
        
        # making the user inactive (kindda ban)
        user.is_active = False
        await db.commit()

        return {
            'code':200,
            'message':f'{username} banned successfully',
            'user':{
                    'id':user.id,
                    'name':user.name,
                    'username':user.username,
                    'email':user.email,
                    'active':user.is_active
                }
        }
    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error while banning user: {e}")

    
# for unbanning the user

@router.patch("/unban-user/{username}")
async def unban_user(username: str, _ : None = Depends(admin_required),
                     db: AsyncSession = Depends(get_async_db)):
    
    try:
        user = await db.execute(
            select(UserModal).where(UserModal.username == username)
        )
        user = user.scalar_one_or_none()

        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                f"{username} doesn't exists")
        
        if not user.is_active:
            user.is_active = True
            await db.commit()
            return {
                'code':200,
                'message':'User is Unbanned Now',
                'user':{
                    'id':user.id,
                    'name':user.name,
                    'username':user.username,
                    'email':user.email,
                    'active':user.is_active
                }
            }
        else:
            return {
                'code':200,
                'message': "user is already unbanned",
                'user':{
                    'id':user.id,
                    'name':user.name,
                    'username':user.username,
                    'email':user.email,
                    'active':user.is_active
                }
            }
        
    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error while Unbanning user: {e}")