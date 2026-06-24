from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from app.core.security import settings
from app.db.models import router as auth_router
from app.api.dependencies import get_current_user

app = FastAPI(
    title="LibStream",
    description="This platform is design to serve the Library System",
    version=settings.version)

app.include_router(auth_router,prefix="/api")

@app.get("/")
def homepage():
    return {'code':'200','message':'Hello,Wolrd!'}

@app.get("/api/protected-data")
async def get_secure_data(current_user: str = Depends(get_current_user)):
    return {'message':f"from {current_user = } you've access to this data "}
