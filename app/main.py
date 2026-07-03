from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from app.core.security import settings
from app.db.auth import router as auth_router
from app.api.dependencies import get_current_user
from app.db.book_operation import router as book_operation
from rough import router as test_router


app = FastAPI(
    title="LibStream",
    description="This platform is design to serve the Library System",
    version=settings.version)

app.include_router(auth_router,prefix="/api")
app.include_router(book_operation,prefix="/operation")
app.include_router(test_router,prefix = "/test")

@app.get("/")
def homepage():
    return {'code':'200','message':'Hello,Wolrd!'}

@app.get("/api/protected-data")
async def get_secure_data(current_user: str = Depends(get_current_user)):
    return {'message':f"from {current_user = } you've access to this data "}

