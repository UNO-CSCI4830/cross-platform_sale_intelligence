from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index = True, nullable = False) 
    '''index means faster lookup, longer insertion/updates,
    nullable means it is allowed to have a null/none value, in this case it is not allowed, becuase we need an email'''
    password_hash = Column(String, nullable = False)
    created_at = Column(DateTime, default=datetime.utcnow) # Coordinated Universal Time is 6 hours ahead of CST.
    linked_accounts = relationship("LinkedAccount", back_populates= "user") 

# Connect External Resale Platforms (FR4)
#Side note: Using Oauth2.0 we can only access Ebay and Depop, we can use Graph API for FaceBook, but Mercari and Poshmark have no public API
class LinkedAccount(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    platform_user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="linked_accoounts")

# Represents a resale listing shown on the dashboard (FR5)
class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    # Links listing to a specific user
    user_id = Column(Integer, nullable=False)

    # Basic listing details shown on the dashboard
    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    condition = Column(String, nullable=False)
    platform = Column(String, nullable=False)

    # Listing status (active or sold)
    status = Column(String, default="active")

    created_at = Column(DateTime, default=datetime.utcnow)

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
