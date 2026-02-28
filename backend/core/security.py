import bcrypt
from datetime import datetime


def hash_pwd(password:str, rounds=12) -> bytes:
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    return pwd

def verify_password(password:str,hash:bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash)

