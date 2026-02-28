from core.security import hash_password
from db.models import User
from core.security import verify_password
from sqlalchemy.orm import Session
def create_user(email, password, db):
    """
    Creates a user by adding it to a sqlite table
    """
    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed) #store user email and password hash
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password_hash): #pass the entered password (from login), and the stored password hash to check against
        return user
    else:
        return None #returns none if check fails (password is incorrect)