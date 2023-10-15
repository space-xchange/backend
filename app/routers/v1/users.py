from app.dependencies import get_token_header, get_web3
from dapp.ganache import get_new_account
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sql_app.database import DatabaseSession, engine
from sql_app.model import User, Base
from sqlalchemy.exc import SQLAlchemyError
from app.utils import IdGen, TokenEncode, Hasher, VerifyMismatchError
from typing import Annotated

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
)

Base.metadata.create_all(bind=engine)

Web3Session = Annotated[None, Depends(get_web3)]
UserSession = Annotated[dict, Depends(get_token_header)]

class RegisterUserBase(BaseModel):
    username: str
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "Kodo",
                    "email": "kodo@gmail.com",
                    "password": "12345678"
                }
            ]
        }
    }

class LoginUserBase(BaseModel):
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "kodo@gmail.com",
                    "password": "12345678"
                }
            ]
        }
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: RegisterUserBase, db: DatabaseSession, web3: Web3Session):
    try:
        db_user = User(
            user_id = IdGen.next_id(),
            username = user.username,
            email = user.email,
            password = Hasher.hash(user.password),
            address = get_new_account(web3),
        )
        db.add(db_user)
        db.commit()

        content = {
            "email": db_user.email,
            "username": db_user.username,
            "address": db_user.address,
        }

        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e.__dict__['orig']))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e.__dict__['orig']))


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def get_user(user: LoginUserBase, db: DatabaseSession, response: Response):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None: 
        raise HTTPException(status_code=401, detail="Wrong Email")
    try:
        Hasher.verify(db_user.password, user.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Wrong Password")
    content = {
        "email": db_user.email,
        "username": db_user.username,
        "address": db_user.address,
    }
    encoded = TokenEncode(content)
    response.set_cookie(key="token", value=encoded, httponly=True)
    return content

@router.get("/", status_code=200)
async def auth(user: UserSession):
    return user

@router.get("/logout", status_code=200)
async def logout(response: Response):
    response.set_cookie(key="token", value="", httponly=True)
    return
