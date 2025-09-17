from fastapi import FastAPI
from backend.routes import detect
app = FastAPI(title="Social Engineering Detection API")

app.include_router(detect.router, prefix="/api")
@app.get("/")
def home():
    return {"message": "Hello from FastAPI backend!"}

