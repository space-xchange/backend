from fastapi import APIRouter

from . import users
# from . import auth

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

router.include_router(users.router)
