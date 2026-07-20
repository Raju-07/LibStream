#fastapi and sqlalchemy
import logging

from fastapi import HTTPException,status,APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select,update,and_
from sqlalchemy.orm import joinedload

#app imports
from app.db.session import get_async_db
from app.api.dependencies import get_current_user,is_book_exists
from app.models import BookAssignModal,UserModal,BooksModal,BookRequestModal
from app.schemas import UserResponse,BookRequest

#router for all the operation (endpoints) in this file.
router = APIRouter(prefix='/users/me',tags=["Users Operation"])
logger = logging.getLogger("app")
db_logger = logging.getLogger("app.database")

# Retrieving the books i'm requested for
@router.get("/book-requests",status_code=status.HTTP_200_OK)
async def list_my_book_requests(user: UserModal = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
    try:
        logger.info("Listing book requests for user %s", user.id)
        result = await db.execute(select(BookRequestModal).where(BookRequestModal.request_by == user.id))
        books = result.scalars().all()
        if not books:
            logger.info("User %s has no book requests", user.id)
            return {
            'code':200,
            'message':"You haven't requested any book yet.",
            'books': books
        }
        
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
            f"Error while retrieving my requested books"
        )
    
# Books that a user ever booked (assigned to user)
@router.get("/loans", status_code=status.HTTP_200_OK)
async def list_my_loans(
    user: UserResponse = Depends(get_current_user),  # Already authenticated user object
    db: AsyncSession = Depends(get_async_db)
):
    try:
        logger.info("Listing loans for user %s", user.id)
        user_id = user.id  # Adjust based on your user structure
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        # books assigned to this user
        stmt = select(BookAssignModal).options(
            joinedload(BookAssignModal.book),
        ).where(BookAssignModal.user_id == user_id)
        results = await db.execute(stmt)
        my_books = results.scalars().all()
        
        # Check if books found
        if not my_books:
            logger.info("User %s has no active loans", user.id)
            return {
                "code": 200,
                "message": "No books assigned to you",
                "books": []
            }
        
        books = [
            {
                "No.": a.index,
                "book": {
                    "id": a.book.id,
                    "name": a.book.name,
                    "author": a.book.author,
                    "category": a.book.category,
                    "location": a.book.location,
                    "returned": a.is_return,
                    "expired_at": a.expired_at.strftime("%d-%m-%Y %H:%M:%S"),
                }
            }
            for a in my_books
        ]
        
        logger.info("Returned %s loan(s) for user %s", len(my_books), user.id)
        return {
            "code": 200,
            "message": "Books retrieved successfully",
            "count": len(my_books),
            "books": books
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve books."
        )

# Request For new Book
@router.post("/book-requests",status_code=status.HTTP_201_CREATED)
async def create_book_request(new_book: BookRequest,user: UserModal = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
    try:
        logger.info("Creating book request for user %s", user.id)
        book = BookRequestModal(**new_book.model_dump())
        book.request_by = user.id
        db.add(book)
        await db.commit()
        await db.refresh(book)

        logger.info("Book request created with id %s", book.id)
        return book
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while requesting new book"
        )

# endpoint to return the book to libstream (Libraray)
@router.put("/loans/{id}/return",status_code=status.HTTP_200_OK)
async def return_book_loan(id:int = Depends(is_book_exists), db: AsyncSession = Depends(get_async_db),user: UserResponse = Depends(get_current_user)):
    logger.info("Return request received for book %s by user %s", id, user.id)
    conditions = [BookAssignModal.user_id == user.id, BookAssignModal.book_id == id,BookAssignModal.is_return==False]
    try:
        stmt = select(BookAssignModal).where(and_(*conditions))
        result = await db.execute(stmt)
        books = result.scalar_one()

        if books:
        
            await db.execute(update(BookAssignModal).where(*conditions).values(is_return=True))
            await db.execute(update(BooksModal).where(BooksModal.id == id).values(is_assigned = False))
            await db.commit()

        logger.info("Book %s returned by user %s", id, user.id)
        return {'code':200,
                'message':"Book has been return and notify"}
    
    except NoResultFound:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "No book found to return back"
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while Returning Book"
        )
        
# borrow any books that available
@router.post("/loans/{id}",status_code=status.HTTP_200_OK)
async def checkout_book(id: int = Depends(is_book_exists),current_user: UserResponse= Depends(get_current_user),
                   db: AsyncSession = Depends(get_async_db)):
    try:
        logger.info("Checkout request received for book %s by user %s", id, current_user.id)
        book = await db.execute(select(BooksModal).where(BooksModal.id == id))
        book = book.scalar_one_or_none()
        if  not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Book isn't Found")
        if book.is_assigned:
            logger.warning("Checkout failed: book %s already assigned", id)
            raise HTTPException(status.HTTP_404_NOT_FOUND,"Book is already taken (Not Available)")
        
        book.is_assigned = True
        await db.commit()
        
        book_assinged = BookAssignModal(
            user_id= current_user.id,
            book_id=book.id
        )
        db.add(book_assinged)
        await db.commit()

        logger.info("Book %s checked out successfully for user %s", id, current_user.id)
        return {
            'code':200,
            'message':"Book assigned to you",
            "book":book
        }
    except HTTPException:
        raise 

    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error occur while book assigning")

