from fastapi import APIRouter

from . import users

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

router.include_router(users.router)
