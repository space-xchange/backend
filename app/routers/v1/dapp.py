from app.dependencies import get_token_header, get_web3, get_contract_instance
from dapp.ganache import get_balance
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sql_app.database import DatabaseSession, engine
from sql_app.model import User, Crypto, CryptoValue, Base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.utils import IdGen, TokenEncode, Hasher, VerifyMismatchError
from typing import Annotated
from datetime import datetime

router = APIRouter(
    prefix="/dapp",
    tags=["dapp"],
    responses={404: {"description": "Not found"}},
)

Base.metadata.create_all(bind=engine)

Web3Session = Annotated[None, Depends(get_web3)]
ContractSession = Annotated[None, Depends(get_contract_instance)]
UserSession = Annotated[dict, Depends(get_token_header)]

class CryptoBase(BaseModel):
    crypto: str
    amount: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "crypto": "eth",
                    "amount": 15
                }
            ]
        }
    }


@router.get("/balance")
async def get_user_balance(user: UserSession, web3: Web3Session):
    return get_balance(web3, user['address']) / (10 ** 18)

@router.post("/buy")
async def buy_asset(crypto_req: CryptoBase, user: UserSession, web3: Web3Session, contract: ContractSession, db: DatabaseSession):
    cur = datetime.now()
    cur_hour = cur.hour % 12
    if cur_hour == 0:
        cur_hour = 12

    crypto = db.query(Crypto).options(joinedload(Crypto.values)).filter(Crypto.name == crypto_req.crypto).first()

    if crypto is None: 
        raise HTTPException(status_code=404, detail="Unknown Crypto")

    current_balance = get_balance(web3, user['address'])
    crypto_price = [value.value_eth for value in crypto.values if int(value.time) == cur_hour][0]
    cost_in_ether = crypto_req.amount * crypto_price

    if current_balance < cost_in_ether:
        raise HTTPException(status_code=400, detail="Insufficient Ether balance.")

    try:
        transaction = contract.functions.buy_crypto(crypto_req.crypto, crypto_req.amount, int(crypto_price * 10 ** 18)).transact({"from": user['address'], "value": web3.to_wei(cost_in_ether, "ether")})
        receipt = web3.eth.wait_for_transaction_receipt(transaction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buying: {str(e)}")

    # Check if transaction was successful
    if not receipt.status:
        raise HTTPException(status_code=500, detail="Transaction failed.")

    return get_balance(web3, user['address']) / (10 ** 18)

@router.post("/sell")
async def sell_asset(crypto_req: CryptoBase, user: UserSession, web3: Web3Session, contract: ContractSession, db: DatabaseSession):
    cur = datetime.now()
    cur_hour = cur.hour % 12
    if cur_hour == 0:
        cur_hour = 12

    crypto = db.query(Crypto).options(joinedload(Crypto.values)).filter(Crypto.name == crypto_req.crypto).first()
    if crypto is None: 
        raise HTTPException(status_code=404, detail="Unknown Crypto")

    crypto_balance = contract.functions.get_crypto_balance(user['address'], crypto_req.crypto).call()

    if crypto_balance < crypto_req.amount:
        raise HTTPException(status_code=400, detail=f"Insufficient {crypto_req.crypto} balance.")

    crypto_price = [value.value_eth for value in crypto.values if int(value.time) == cur_hour][0]
    cost_in_ether = crypto_req.amount * crypto_price

    try:
        transaction = contract.functions.sell_crypto(crypto_req.crypto, crypto_req.amount, int(crypto_price * 10 ** 18)).transact({"from": user['address']})
        receipt = web3.eth.wait_for_transaction_receipt(transaction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selling: {str(e)}")

    # Check if transaction was successful
    if not receipt.status:
        raise HTTPException(status_code=500, detail="Transaction failed.")

    return get_balance(web3, user['address']) / (10 ** 18)

@router.get("/transactions")
async def get_transactions(user: UserSession, web3: Web3Session, contract: ContractSession, db: DatabaseSession):
    # Get Sold and Purchased events for the user
    try:
        # sold_events = contract.events.Sold().get_logs(fromBlock=0, toBlock="latest")
        # purchased_events = contract.events.Purchased().get_logs(fromBlock=0, toBlock="latest")
        sold_events = contract.events.Sold.create_filter(fromBlock=0, argument_filters={'seller': user['address']}).get_all_entries()
        purchased_events = contract.events.Purchased.create_filter(fromBlock=0, argument_filters={'buyer': user['address']}).get_all_entries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

    # Convert events to a more friendly format
    print(sold_events)
    print(purchased_events)
    sold_data = [{"type": "sell", "blockNumber": event['blockNumber'], "crypto": event['args']['ticker'], "total": event['args']['total_received']} for event in sold_events]
    purchased_data = [{"type": "purchase", "blockNumber": event['blockNumber'], "crypto": event['args']['ticker'], "total": event['args']['total_cost']} for event in purchased_events]

    # Merge and sort events by block number
    all_transactions = sorted(sold_data + purchased_data, key=lambda x: x['blockNumber'])

    return all_transactions
