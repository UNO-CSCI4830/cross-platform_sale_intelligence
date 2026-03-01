from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index = True, nullable = False) 
    '''index means faster lookup, longer insertion/updates,
    nullable means it is allowed to have a null/none value, in this case it is not allowed, becuase we need an email'''
    password_hash = Column(String, nullable = False)
    created_at = Column(DateTime, default=datetime.utcnow) # Coordinated Universal Time is 6 hours ahead of CST.

# Represents a user-submitted issue or problem report
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)  
    # Optional email so users can be contacted if needed
    email = Column(String, nullable=True)

    # Description of the problem reported by the user
    message = Column(String, nullable=False)

    # Timestamp for when the issue was submitted
    created_at = Column(DateTime, default=datetime.utcnow)
