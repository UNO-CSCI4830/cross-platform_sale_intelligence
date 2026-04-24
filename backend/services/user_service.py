from sqlalchemy.orm import Session
from backend.db.models import User
from backend.core.security import hash_password, verify_password
from fastapi import HTTPException


def create_user(email, first_name, last_name, password, db):
    """Creates a new user and saves them to the database."""
    hashed = hash_password(password)
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(email: str, password: str, db: Session):
    """Returns the User if credentials are valid, otherwise None."""
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def update_email(user_id: int, new_email: str, db: Session):
    """FR14: Update a user's email address."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = new_email
    db.commit()
    db.refresh(user)


def change_password(user_id: int, current_password: str, new_password: str, db: Session):
    """FR3: Verify the current password and replace it with a new one."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    if verify_password(new_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the current password",
        )

    user.password_hash = hash_password(new_password)
    db.commit()