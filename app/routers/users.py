from app.dependencies import get_token_header
from fastapi import APIRouter, Depends, HTTPException, FastAPI, Request, HTTPException, status, Cookie, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated
from sql_app.database import SessionLocal, engine
from sql_app.model import User, Base
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pprint import pprint
import jwt
from app.utils import ID_GEN, HASHER, KEY

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

Base.metadata.create_all(bind=engine)

class RegisterUserBase(BaseModel):
    username: str
    email: str
    password: str

class LoginUserBase(BaseModel):
    email: str
    password: str
    
def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_database_session)]

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: RegisterUserBase, db: db_dependency):
    try:
        db_user = User(
            user_id = ID_GEN.next_id(),
            username = user.username,
            email = user.email,
            password = HASHER.hash(user.password),
        )
        db.add(db_user)
        db.commit()

        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e.__dict__['orig']))

@router.post("/login", status_code=status.HTTP_201_CREATED)
async def get_user (user: LoginUserBase, db: db_dependency, response: Response):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user == None: 
        raise HTTPException(status_code=404, detail="Wrong Email")
    if not HASHER.verify(db_user.password, user.password):
        raise HTTPException(statuscode=404, detail="Wrong Password")
    content = {
        "email": db_user.email,
        "username": db_user.username,
    }
    encoded = jwt.encode(content, KEY, algorithm="HS256")
    response.set_cookie(key="token", value=encoded, httponly=True)
    return content
    
@router.get("/{username}")
async def get_user (username: str, db: db_dependency):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user == None: 
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



