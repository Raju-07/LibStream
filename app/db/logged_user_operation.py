from fastapi import HTTPException,status,APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,and_,or_
from app.db.session import get_async_db
from app.api.dependencies import get_current_user
from app.models import BookAssignModal,UserModal
from app.schemas import BookResponse,UserResponse

router = APIRouter(prefix='/user',tags=["Users Operation"])

@router.get("/my-books", status_code=status.HTTP_200_OK)
async def get_my_books(
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
        
        # Query books assigned to this user
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
        raise  HTTPException(status.HTTP_400_BAD_REQUEST,
                             "Operation Failed") # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve books: {str(e)}"
        )
