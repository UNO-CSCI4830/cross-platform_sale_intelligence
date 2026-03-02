from sqlalchemy.orm import Session
from backend.db.models import User
from backend.core.security import hash_pwd, verify_password

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
    if user and verify_password(password, user.password_hash):
        return user
    return None
