from fastapi import APIRouter, HTTPException
from sql_app.database import DatabaseSession, engine
from sql_app.model import Crypto, Base
from sqlalchemy.orm import joinedload

router = APIRouter( 
    prefix="/crypto",
    tags=["crypto"],
    responses={404: {"description": "Not found"}},
)

Base.metadata.create_all(bind=engine)

@router.get("/")
async def get_all_cryptos(db: DatabaseSession):
    cryptos = db.query(Crypto).options(joinedload(Crypto.values)).all()
    return cryptos

@router.get("/{crypto_name}")
async def get_crypto(db: DatabaseSession, crypto_name: str):
    crypto = db.query(Crypto).options(joinedload(Crypto.values)).filter(Crypto.name == crypto_name).first()

    if crypto is None: 
        raise HTTPException(status_code=404, detail="Unknown Crypto")

    return crypto
