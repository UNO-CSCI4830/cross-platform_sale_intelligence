import bcrypt
from datetime import datetime

#handler functions
def hash_pwd(password:str, rounds=12) -> bytes:
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    return pwd

def check_pwd(password:str,hash:bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash)

class UserAuth:
    def __init__(self):
        self.users = {} #Using tuple as a placeholder until database is implemented

    def add_user(self, username:str, password:str) -> bool:
        if username in self.users: #Is username already taken? Return HTMLException
            return False
        self.users[username] = {
            'pwd_hash': hash_pwd(password),
            'created_at': datetime.now(),
            'pwd_rounds': 12
        }
        return True
    
    def login(self, username:str, password:str):
        pass