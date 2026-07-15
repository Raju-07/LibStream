from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import init_db,close_db
from app.core.security import settings
from app.db.auth import router as auth_router
from app.api.dependencies import get_current_user
from app.db.books_user_operation import router as book_operation
from contextlib import asynccontextmanager
from app.schemas import UserResponse
from app.crud import router as admin_crud_route
from app.db.logged_user_operation import router as user_router
# from rough import router as test_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database")
    await init_db()
    print("database initialized and verified ")
    yield
    print("Closing db")
    await close_db()
    print("DB closed ")

app = FastAPI(lifespan=lifespan ,
    title="LibStream",
    description="This platform is design to serve the Library System",
    version=settings.version)

app.include_router(auth_router,prefix="/api")
app.include_router(book_operation,prefix="/operation")
app.include_router(admin_crud_route)
app.include_router(user_router)
# app.include_router(test_router,prefix = "/test")

@app.get("/")
async def homepage():
    return {'code':'200','message':'Hello,Wolrd!'}

@app.get("/api/protected-data")
async def get_secure_data(current_user: UserResponse = Depends(get_current_user)):
    return {'message':f"from {current_user.id} you've access to this data "}

