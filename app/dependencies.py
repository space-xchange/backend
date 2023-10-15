from typing import Annotated
from fastapi import Cookie, HTTPException, status
from sql_app.model import User

from app.utils import TokenDecode

from dapp import ganache
from dapp.contract import compile_contract

from os import path

async def get_token_header(token: Annotated[str | None, Cookie()]):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="There is no token")
    try:
        decoded = TokenDecode(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

web3 = ganache.get_web3()
assert web3.is_connected()

contract_abi, contract_bytecode = compile_contract(
    path.join(
        path.dirname(__file__),
        "../dapp/contracts/SpaceExchange.sol"
    )
)

contract = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
tx_hash = contract.constructor().transact({'from': web3.eth.accounts[0]})
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
contract_instance = web3.eth.contract(address=tx_receipt['contractAddress'], abi=contract_abi)

async def get_web3():
    return web3

async def get_contract_instance():
    return contract_instance
