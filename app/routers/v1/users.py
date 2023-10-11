from app.dependencies import get_token_header
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sql_app.database import DatabaseSession, engine
from sql_app.model import User, Base
from sqlalchemy.exc import SQLAlchemyError
from app.utils import IdGen, TokenEncode, Hasher, VerifyMismatchError

router = APIRouter( prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

Base.metadata.create_all(bind=engine)

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
                    "password": "P@55w.rd"
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
                    "password": "P@55w.rd"
                }
            ]
        }
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: RegisterUserBase, db: DatabaseSession):
    try:
        db_user = User(
            user_id = IdGen.next_id(),
            username = user.username,
            email = user.email,
            password = Hasher.hash(user.password),
        )
        db.add(db_user)
        db.commit()

        content = {
            "email": db_user.email,
            "username": db_user.username,
        }

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
    encoded = TokenEncode(content)
    response.set_cookie(key="token", value=encoded, httponly=True)
    return content
