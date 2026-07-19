#dependency imports
import logging
from contextlib import asynccontextmanager

#fastapi & sqlalchemy imports
from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession

#app imports
from app.core.database import init_db,close_db
from app.core.security import settings
from app.db.auth import router as auth_router
from app.api.dependencies import get_current_user
from app.db.non_user_operation import router as book_operation
from app.schemas import UserResponse
from app.admin_operations import router as admin_crud_route
from app.db.user_operation import router as user_router
from app.logging_config import setup_logging

# Initalizing LOGGER_SETUP
setup_logging(settings.debug)
logger = logging.getLogger("app") #app logger
db_logger = logging.getLogger("app.database") #database logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_logger.debug("Database- initializing...")
    await init_db()
    db_logger.info("Database- initialized and verified.")
    yield
    db_logger.debug("Database- closing....")
    await close_db()
    db_logger.info("Database- closed.")

app = FastAPI(lifespan=lifespan ,
    title="LibStream",
    description="This platform is design to serve the Library System",
    version=settings.version)


@app.on_event("startup")
async def startup_event():
    logger.info("Application Statup")

app.include_router(auth_router,prefix="/api")
app.include_router(book_operation,prefix="/operation")
app.include_router(admin_crud_route)
app.include_router(user_router)
# app.include_router(test_router,prefix = "/test")

@app.get("/")
async def homepage():
    logger.info("Getting Route message \n")
    return {'code':'200','message':'Hello,Wolrd!'}

@app.get("/api/protected-data")
async def get_secure_data(current_user: UserResponse = Depends(get_current_user)):
    return {'message':f"from {current_user.id} you've access to this data "}

