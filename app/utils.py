from sonyflake import SonyFlake
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from paseto.protocol.version4 import decrypt, encrypt
import os
from msgpack import unpackb, packb

IdGen = SonyFlake()

Hasher = PasswordHasher()

def TokenEncode(content):
    return encrypt(packb(content), bytes(os.environ['KEY'], 'ascii')).decode()

def TokenDecode(content):
    return unpackb(decrypt(bytes(content, 'ascii'), bytes(os.environ['KEY'], 'ascii')))
