from app.api.dependencies import get_admin_user
from sqlalchemy import select,and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,APIRouter
from app.schemas import BookRequest
from app.db.session import get_async_db

router = APIRouter(prefix='admin',tags=["Admin Operations"])

@router.post('/add-book')
async def add_book(
    book:BookRequest,
    admin_user : AsyncSession = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_db)
    ):
    
    return book