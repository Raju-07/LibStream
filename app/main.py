from fastapi import FastAPI


app = FastAPI(title="LibStream",description="This platform is design to serve the Library System")

@app.get("/")
def homepage():
    return {'code':'200','message':'Hello,Wolrd!'}
