from fastapi import FastAPI
from core.security import settings

app = FastAPI(
    title="LibStream",
    description="This platform is design to serve the Library System",
    version=settings.version)

@app.get("/")
def homepage():
    return {'code':'200','message':'Hello,Wolrd!'}
