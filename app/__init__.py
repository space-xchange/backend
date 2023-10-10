from fastapi import FastAPI
from app.routers import v1

app = FastAPI()

app.include_router(v1.router)
