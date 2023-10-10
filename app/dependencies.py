from typing import Annotated
import jwt
from fastapi import Cookie, HTTPException
from sql_app.model import User
from app.utils import KEY

async def get_token_header(token: Annotated[str | None, Cookie()]):
	try:
		decoded = jwt.decode(token, KEY, algorithms="HS256")
		print(decoded)
	except Exception as e: 
		print(e)