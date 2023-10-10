from sonyflake import SonyFlake
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
KEY = "secret"
ID_GEN = SonyFlake()

Hasher = PasswordHasher()
