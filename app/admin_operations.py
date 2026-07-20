#dependency imports
import logging
from datetime import timezone,datetime

#Fastapi & sqlalchemy
from sqlalchemy import select,delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,APIRouter,HTTPException,status

#app imports
from app.api.dependencies import admin_required,is_book_exists
from app.schemas import AddBookRequest,UpdateBookRequest,UserRegister,AdminUserResponse,ViewBookResponse
from app.db.session import get_async_db
from app.models import BooksModal,UserModal,BookRequestModal,BookRequestStatus,BookAssignModal,BookCategory
from app.db.non_user_operation import get_book_by_id
from app.db.auth import create_user

#admin operation routes
router = APIRouter(prefix='/admin',tags=["Admin Operations"])
logger = logging.getLogger("app")
db_logger = logging.getLogger("app.database")

# retrieve all user
@router.get("/users",status_code=status.HTTP_200_OK,response_model=list[AdminUserResponse])
async def list_users(_:None = Depends(admin_required),db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(
            select(UserModal.name,UserModal.id,UserModal.username,
                   UserModal.email,UserModal.is_active,UserModal.is_admin))
        users = result.mappings().all()

        if not users:
            logger.warning("No users found")
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                "No users found")

        return users
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while Retrieving users: {e}"
        )
    
#retrieving banned user's
@router.get("/banned-users",response_model=list[AdminUserResponse],status_code=status.HTTP_200_OK)
async def list_banned_users(_:None = Depends(admin_required), db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(
            select(UserModal.name,UserModal.id,UserModal.username,UserModal.email,UserModal.is_active,UserModal.is_admin).
            where(
                UserModal.is_active == False
            ))
        users = result.mappings().all()

        if not users:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "No user is banned Now"
            )
        
        return users
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while retrieving banned users: {e}"
        )
    
# Get all Requested books
@router.get("/book-requests",status_code=status.HTTP_200_OK)
async def list_book_requests(_:None=Depends(admin_required),db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(select(BookRequestModal.id,BookRequestModal.name,BookRequestModal.author,BookRequestModal.request_by,BookRequestModal.description,BookRequestModal.created_at,BookRequestModal.edition))
        books =result.mappings().all()
        if not books:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "No Books Found"
            )
        
        return {
            'code':200,
            'message':'Requested Books',
            'books':books
        }
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while Retrieving books: {str(e)}"
        )
    
# Getting Requested Books by status
@router.get("/book-requests/{status}")
async def list_books_by_status(requests_status:BookRequestStatus,_:None = Depends(admin_required),db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(select(BookRequestModal).where(BookRequestModal.status == requests_status))
        books = result.scalars().all()

        if not books:
           raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "No Books Found"
            )
        
        return {
            'code':200,
            'message':f"Books with {status}",
            'books':books
        }
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while Retrieving books: {str(e)}"
        )
    
# Getting all the books that has not been return after last date
@router.get("/overdue-loans")
async def list_overdue_loans(
    db: AsyncSession = Depends(get_async_db),
    _: None = Depends(admin_required)
):
    try:
        result = await db.execute(
            select(BookAssignModal)
            .options(
                joinedload(BookAssignModal.book),   # load book info
                joinedload(BookAssignModal.user)    # load user info
            )
            .where(BookAssignModal.expired_at < datetime.now(timezone.utc))
            .where(BookAssignModal.is_return == False)   # only not returned
        )
        assignments = result.scalars().all()

        if not assignments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Books Found"
            )

        # Build response with book + user details
        books = [
            {
                "assign_id": a.index,
                "expired_at": a.expired_at,
                "book": {
                    "id": a.book.id,
                    "name": a.book.name,
                    "author": a.book.author,
                    "category": a.book.category,
                    "location": a.book.location,
                },
                "user": {
                    "id": a.user.id,
                    "name": a.user.name,
                    "username": a.user.username,
                    "email": a.user.email,
                    "is_active": a.user.is_active,
                    "is_admin": a.user.is_admin,
                }
            }
            for a in assignments
        ]

        return {
            "code": 200,
            "message": "Books not returned after due date.",
            "books": books
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while retrieving books: {e}"
        )
    
@router.post('/book',response_model=ViewBookResponse)
async def create_book(
    book:AddBookRequest,
    _ : None = Depends(admin_required),
    db: AsyncSession = Depends(get_async_db),
    ):
    try:
        logger.info("Admin creating book: %s", book.name)
        new_book = BooksModal(**book.model_dump())
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate entry")
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    logger.info("Book created successfully: %s", new_book.id)
    return new_book

#created new user (reusing existing function to create new user)
@router.post("/users/admin",status_code=status.HTTP_201_CREATED)
async def create_admin_user(user: UserRegister, db: AsyncSession = Depends(get_async_db), _ : None = Depends(admin_required)):
    try:
        admin_user = await create_user(user, db)
        admin_user.is_admin = True
        await db.commit()
        
        return {
            'code':200,
            'message':"User created with admin previleges.",
            'user':{
                'id':admin_user.id,
                'username':admin_user.username,
                'is_admin': admin_user.is_admin
            }
        }
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error while creating admin user {e}")


@router.patch("/books/{id}",status_code=status.HTTP_200_OK)
async def update_book_details(book: UpdateBookRequest ,id: int = Depends(is_book_exists),
                       db: AsyncSession = Depends(get_async_db),
                       _:None = Depends(admin_required)):
    # updating book
    try:
        logger.info("Admin updating book: %s", id)
        result = await db.execute(select(BooksModal).where(BooksModal.id == id))
        exists_book = result.scalar_one_or_none()

        #unpacking all the data to it's column
        data_update = book.model_dump(exclude_unset=True)
        data_update = {k:v for k,v in data_update.items() if v != ''} # filter data with values - ''
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
@router.patch("/{username}/ban")
async def deactivate_user(username: str,_ : None = Depends(admin_required),
                   db: AsyncSession = Depends(get_async_db)):
    try:
        logger.info("Admin banning user: %s", username)
        user = await db.execute(select(UserModal).where(UserModal.username == username))
        user = user.scalar_one_or_none()

        if not user.is_active:
            logger.info("User already banned: %s", username)
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

@router.patch("/{username}/unban")
async def activate_user(username: str, _ : None = Depends(admin_required),
                     db: AsyncSession = Depends(get_async_db)):
    
    try:
        logger.info("Admin unbanning user: %s", username)
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
    


@router.delete("/books/{id}")
async def delete_book(id:int = Depends(get_book_by_id),
                            db: AsyncSession = Depends(get_async_db),
                            _: None = Depends(admin_required)):
    
    try:
        logger.info("Admin deleting book: %s", id)
        await db.execute(delete(BooksModal).where(BooksModal.id == id))
        await db.commit()
        logger.info("Book deleted successfully: %s", id)
        return {'code':200,
                'Message':"Book Deleted Successfully"}
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deletation Failed due to {e}"
        )

    

# Deleting user
@router.delete("/users/{username}",status_code = status.HTTP_200_OK)
async def delete_user_account(username:str,db: AsyncSession = Depends(get_async_db),_:None=Depends(admin_required)):
    try:
        logger.info("Admin deleting user: %s", username)
        result = await db.execute(select(UserModal).where(UserModal.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                    f"user '{username}' not found to delete.")
        
        await db.delete(user)
        await db.commit()
        return {
            'code':200,
            'message': f"User {username} Account Deleted."
        }
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error while deleting user: {e}")

