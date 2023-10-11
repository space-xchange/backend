from sonyflake import SonyFlake
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from paseto.protocol.version4 import decrypt, encrypt
import os

IdGen = SonyFlake()

Hasher = PasswordHasher()

def TokenEncode(content):
    return encrypt(content, os.environ['KEY'])

def TokenDecode(content):
    return decrypt(content, os.environ['KEY'])
