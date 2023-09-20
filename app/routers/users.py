from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_token_header

router = APIRouter(
	prefix="/users",
	tags=["users"],
	# dependencies=[Depends(get_token_header)],
	responses={404: {"description": "Not found"}},
)

fake_db = [{"username": "newbee"}, {"username": "kodo"}]

@router.get("")
@router.get("/")
async def read_users():
	return fake_db


@router.get("/me")
async def read_user_me():
	return {"username": "fakecurrentuser"}


@router.get("/{username}")
async def read_user(username: str):
	if not any(user for user in fake_db if user['username'] == username):
		raise HTTPException(status_code=404, detail="User not found")
	return {"username": username}