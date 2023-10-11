from typing import Annotated
from fastapi import Cookie, HTTPException, status
from sql_app.model import User

from app.utils import TokenDecode

async def get_token_header(token: Annotated[str | None, Cookie()]):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="There is no token")
    try:
        decoded = TokenDecode(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
