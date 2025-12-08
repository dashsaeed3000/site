from passlib.hash import bcrypt
from typing import Tuple


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    return bcrypt.verify(password, hash_)
