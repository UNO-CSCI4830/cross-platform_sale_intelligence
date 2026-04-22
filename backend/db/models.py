from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String(255), unique = True, index = True, nullable = False) 
    '''index means faster lookup, longer insertion/updates,
    nullable means it is allowed to have a null/none value, in this case it is not allowed, becuase we need an email'''
    first_name = Column(String(255), unique = False, nullable = False)
    last_name = Column(String(255), unique = False, nullable = False)
    password_hash = Column(String(255), nullable = False)
    created_at = Column(DateTime, server_default=func.now()) 
    linked_accounts = relationship("LinkedAccount", back_populates= "user", cascade="all, delete")
    listings = relationship("ListingSnapshot", back_populates="user")

# Connect External Resale Platforms (FR4)
#Side note: Using Oauth2.0 we can only access Ebay and Depop, we can use Graph API for FaceBook, but Mercari and Poshmark have no public API
class LinkedAccount(Base):
    __tablename__ = "linked_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(255), nullable=False)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    platform_user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="linked_accounts")


class ListingSnapshot(Base):
    __tablename__ = "listing_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(255), nullable=False)              # "ebay", "depop"
    platform_listing_id = Column(String(255), nullable=False)   # listing's ID on eBay
    title = Column(String(255), nullable=True)
    price = Column(Numeric(10,2), nullable=True)
    quantity = Column(Integer, nullable=True)
    condition = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)                 # "active", "sold", 
    item_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    captured_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="listings")

# Represents a user-submitted issue or problem report
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)  
    # Optional email so users can be contacted if needed
    email = Column(String(255), nullable=True)

    # Description of the problem reported by the user
    message = Column(String(255), nullable=False)

    # Timestamp for when the issue was submitted
    created_at = Column(DateTime, default=datetime.utcnow)

