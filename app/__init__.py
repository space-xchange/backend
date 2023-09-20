import uvicorn
from fastapi import FastAPI
from app.routers import users

app = FastAPI()

print(users.router)

app.include_router(users.router)

@app.get("/")
async def root():
	return {"message": "Hello Bigger Applications!"}