from fastapi import APIRouter, HTTPException
from sql_app.database import DatabaseSession, engine
from sql_app.model import Crypto, Base
from sqlalchemy.orm import joinedload
from datetime import datetime

router = APIRouter( 
    prefix="/crypto",
    tags=["crypto"],
    responses={404: {"description": "Not found"}},
)

Base.metadata.create_all(bind=engine)

@router.get("/")
async def get_all_cryptos(db: DatabaseSession):
    raw_cryptos = db.query(Crypto).options(joinedload(Crypto.values)).all()

    cryptos = []

    start_id = raw_cryptos[0].values[0].id
    cur = datetime.now().hour
    if cur < start_id:
        cur += 12
    end = cur - start_id - 1
    if end == 0:
        end = 12

    for raw_crypto in raw_cryptos:
        raw_crypto.img = f"https://www.gemini.com/images/currencies/icons/default/{raw_crypto.name}.svg"
        raw_crypto.diff = (raw_crypto.values[cur - start_id].value_aud - raw_crypto.values[end].value_aud) / raw_crypto.values[cur - start_id].value_aud * 100 * 100
        cryptos.append(raw_crypto)

    return cryptos

@router.get("/{crypto_name}")
async def get_crypto(db: DatabaseSession, crypto_name: str):
    crypto = db.query(Crypto).options(joinedload(Crypto.values)).filter(Crypto.name == crypto_name).first()

    if crypto is None: 
        raise HTTPException(status_code=404, detail="Unknown Crypto")

    return crypto
