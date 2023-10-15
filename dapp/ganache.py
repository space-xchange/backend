from web3 import Web3, HTTPProvider
import threading

def get_web3():
    return Web3(HTTPProvider("http://127.0.0.1:8545"))

def get_accounts(web3):
    return web3.eth.accounts

def get_contract(web3 ,abi, bytecode):
    return web3.eth.contract(abi=abi, bytecode=bytecode)

def get_balance(web3, address):
    return web3.eth.get_balance(address)

current_index = 1
lock = threading.Lock()

def get_new_account(web3):
    global current_index

    with lock:
        if current_index >= len(web3.eth.accounts):
            raise Exception("Out of demo users")

        current_index += 1
        return web3.eth.accounts[current_index - 1]
