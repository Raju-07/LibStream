#dependency imports
import logging
from contextlib import asynccontextmanager

#fastapi & sqlalchemy imports
from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

#app imports
from app.core.database import init_db,close_db
from app.core.security import settings
from app.db.auth import router as auth_router
from app.api.dependencies import get_current_user
from app.db.non_user_operation import router as book_operation
from app.schemas import UserResponse
from app.models import UserModal,BooksModal
from app.admin_operations import router as admin_crud_route
from app.db.user_operation import router as user_router
from app.logging_config import setup_logging
from app.db.session import get_async_db

# Initalizing LOGGER_SETUP
setup_logging(settings.debug)
logger = logging.getLogger("app") #app logger
db_logger = logging.getLogger("app.database") #database logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_logger.info("Database initialization started")
    await init_db()
    db_logger.info("Database initialized successfully")
    yield
    db_logger.info("Database shutdown started")
    await close_db()
    db_logger.info("Database shutdown complete")

app = FastAPI(lifespan=lifespan ,
    title="LibStream",
    description="This platform is design to serve the Library System",
    version=settings.version)


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")

app.include_router(auth_router,prefix="/api")
app.include_router(book_operation,prefix="/operation")
app.include_router(admin_crud_route)
app.include_router(user_router)
# app.include_router(test_router,prefix = "/test")

@app.get("/")
async def homepage(db:AsyncSession = Depends(get_async_db),user: UserModal = Depends(get_current_user)):
    logger.info("Homepage accessed")
    stmt = select(BooksModal).where(BooksModal.is_assigned == False)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return {
        'code':'200',
        'message':'Welcome to LibStream!',
        'books': books
        }

@app.get("/api/auth/me")
async def get_secure_data(current_user: UserResponse = Depends(get_current_user)):
    return {'message':f"from {current_user.id} you've access to this data "}

