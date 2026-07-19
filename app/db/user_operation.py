#fastapi and sqlalchemy
from fastapi import HTTPException,status,APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select,update,and_

#app imports
from app.db.session import get_async_db
from app.api.dependencies import get_current_user,is_book_exists
from app.models import BookAssignModal,UserModal,BooksModal,BookRequestModal
from app.schemas import UserResponse,BookRequest,ViewBookResponse

#router for all the operation (endpoints) in this file.
router = APIRouter(prefix='/user',tags=["Users Operation"])

# Retrieving the books i'm requested for
@router.get("/my-requested-books",status_code=status.HTTP_200_OK)
async def my_requested_books(user: UserModal = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(select(BookRequestModal).where(BookRequestModal.request_by == user.id))
        books = result.scalars().all()
        if not books:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "No Books Requested"
            )
        
        return {
            'code':200,
            'message':"Requested Books",
            'books': books
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while retrieving my requested books: {str(e)}"
        )
    
# Books that a user ever booked (assigned to user)
@router.get("/my-all-books", status_code=status.HTTP_200_OK)
async def get_my_all_books(
    user: UserResponse = Depends(get_current_user),  # Already authenticated user object
    db: AsyncSession = Depends(get_async_db)
):
    try:
        # Extract user_id from the user object returned by get_current_user
        user_id = user.id  # Adjust based on your user structure
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        # books assigned to this user
        stmt = select(BookAssignModal).where(BookAssignModal.user_id == user_id)
        results = await db.execute(stmt)
        my_books = results.scalars().all()
        
        # Check if books found
        if not my_books:
            return {
                "code": 200,
                "message": "No books assigned to you",
                "books": []
            }
        
        return {
            "code": 200,
            "message": "Books retrieved successfully",
            "count": len(my_books),
            "books": my_books
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve books: {str(e)}"
        )

# Request For new Book
@router.post("/requrest-new-book",status_code=status.HTTP_201_CREATED)
async def request_new_book(new_book: BookRequest,user: UserModal = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
    try:
        book = BookRequestModal(**new_book.model_dump())
        book.request_by = user.id
        db.add(book)
        await db.commit()
        await db.refresh(book)

        return book
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while Requesting new Book: {str(e)}"
        )

# endpoint to return the book
@router.put("/book-return/{id}",status_code=status.HTTP_200_OK)
async def return_book(id:int = Depends(is_book_exists), db: AsyncSession = Depends(get_async_db),user: UserResponse = Depends(get_current_user)):
    conditions = [BookAssignModal.user_id == user.id, BookAssignModal.book_id == id,BookAssignModal.is_return==False]
    try:
        stmt = select(BookAssignModal).where(and_(*conditions))
        result = await db.execute(stmt)
        books = result.scalar_one()

        if books:
        
            await db.execute(update(BookAssignModal).where(*conditions).values(is_return=True))
            await db.execute(update(BooksModal).where(BooksModal.id == id).values(is_assigned = False))
            await db.commit()

        return {'code':200,
                'message':"Book has been return and notify"}
    
    except NoResultFound:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "No book found to return"
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while Returning Book {str(e)}"
        )
        
# Taking any book to books that available
@router.patch("/take-book/{id}",status_code=status.HTTP_200_OK)
async def take_book(id: int = Depends(is_book_exists),current_user: UserResponse= Depends(get_current_user),
                   db: AsyncSession = Depends(get_async_db)):
    try:
        book = await db.execute(select(BooksModal).where(BooksModal.id == id))
        book = book.scalar_one_or_none()
        if  not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Book isn't Found")
        if book.is_assigned:
            raise HTTPException(status.HTTP_404_NOT_FOUND,"Book is already taken (Not Available)")
        
        book.is_assigned = True
        await db.commit()
        
        book_assinged = BookAssignModal(
            user_id= current_user.id,
            book_id=book.id
        )
        db.add(book_assinged)
        await db.commit()

        return {
            'code':200,
            'message':"Book assigned to you",
            "book":book
        }
    except HTTPException:
        raise 

    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error occur while book assigning: {e}")

