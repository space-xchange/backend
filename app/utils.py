from sonyflake import SonyFlake
from argon2 import PasswordHasher
KEY = "secret"
ID_GEN = SonyFlake()

HASHER = PasswordHasher()