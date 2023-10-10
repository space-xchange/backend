from app.dependencies import get_token_header
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sql_app.database import DatabaseSession, engine
from sql_app.model import User, Base
from sqlalchemy.exc import SQLAlchemyError
from app.utils import ID_GEN, KEY, Hasher, VerifyMismatchError

import jwt

router = APIRouter(
    prefix="/users",
    # dependencies=[Depends(get_token_header)],
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

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: RegisterUserBase, db: DatabaseSession):
    try:
        db_user = User(
            user_id = ID_GEN.next_id(),
            username = user.username,
            email = user.email,
            password = Hasher.hash(user.password),
        )
        db.add(db_user)
        db.commit()

        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e.__dict__['orig']))


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def get_user (user: LoginUserBase, db: DatabaseSession, response: Response):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None: 
        raise HTTPException(status_code=404, detail="Wrong Email")
    try:
        Hasher.verify(db_user.password, user.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=404, detail="Wrong Password")
    content = {
        "email": db_user.email,
        "username": db_user.username,
    }
    encoded = jwt.encode(content, KEY, algorithm="HS256")
    response.set_cookie(key="token", value=encoded, httponly=True)
    return content


@router.get("/{username}")
async def get_user (username: str, db: DatabaseSession):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None: 
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

