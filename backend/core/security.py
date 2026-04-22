import bcrypt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import User
from jose import jwt, JWTError
import os
from cryptography.fernet import Fernet

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #FastAPI looks for the JSON web token in the request header

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Extracts JWT token from request header, decodes it to get user_id, and returns the matching User from the db"""
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"]) #algorithm handles hashing and signature
        user_id = payload.get("sub") #get user_id from subject field
        if user_id is None: #If user_id isn't found
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError: #Catches expired or tampered/invalid tokens
        raise HTTPException(status_code=401, detail="Invalid token")
    #look up user in db using id from token
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def create_access_token(user_id:int) -> str:
    """Create a token that shows 3rd party platform that the user is logged in to our app"""
    payload = {
        "sub": str(user_id), # Who is logged in
        "exp": datetime.utcnow() + timedelta(hours=24) #time until token expires
        #"iat": {some time} (do we want tokens to expire after some event, such as a password change?) #sprint2 task
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256") #jose 


def hash_password(password:str, rounds=12) -> bytes:
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds)).decode('utf-8')
    return pwd

def verify_password(password:str,hash:bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash)

fernet = Fernet(os.getenv("ENCRYPTION_KEY"))
def encrypt_token(token:str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token:str) -> str:
    return fernet.decrypt(token.encode()).decode()


