from fastapi import FastAPI,Depends


app = FastAPI(
    title="LibStream",
    description="This platform is design to serve the Library System",
    version="1.0.0")

@app.get("/")
def homepage():
    return {'code':'200','message':'Hello,Wolrd!'}
