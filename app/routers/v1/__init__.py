from fastapi import APIRouter

from . import users, dapp, crypto

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

router.include_router(users.router)
router.include_router(dapp.router)
router.include_router(crypto.router)
