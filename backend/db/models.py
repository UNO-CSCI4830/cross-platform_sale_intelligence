from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index = True, nullable = False) 
    '''index means faster lookup, longer insertion/updates,
    nullable means it is allowed to have a null/none value, in this case it is not allowed, becuase we need an email'''
    password_hash = Column(String, nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC)) # Coordinated Universal Time is 6 hours ahead of CST.