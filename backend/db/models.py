from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, index = True, nullable = False) 
    '''index means faster lookup, longer insertion/updates,
    nullable means it is allowed to have a null/none value, in this case it is not allowed, becuase we need an email'''
    first_name = Column(String, unique = False, index = True, nullable = False)
    last_name = Column(String, unique = False, index = True, nullable = False)
    password_hash = Column(String, nullable = False)
    created_at = Column(DateTime, default=datetime.utcnow) # Coordinated Universal Time is 6 hours ahead of CST.
    linked_accounts = relationship("LinkedAccount", back_populates= "user") 

# Connect External Resale Platforms (FR4)
#Side note: Using Oauth2.0 we can only access Ebay and Depop, we can use Graph API for FaceBook, but Mercari and Poshmark have no public API
class LinkedAccount(Base):
    __tablename__ = "linked_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    platform_user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="linked_accounts")

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
    category = Column(String, nullable=True)
    size = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    weight_lbs = Column(Float,  nullable=True)
    image_url = Column(String, nullable=True)

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

"""# FR4: Stores external resale platforms linked to a user account
class PlatformConnection(Base):
    __tablename__ = "platform_connections"

    id = Column(Integer, primary_key=True, index=True)

    # User in our system
    user_id = Column(Integer, nullable=False)

    # External platform name such as eBay, Depop, or Poshmark
    platform_name = Column(String, nullable=False)

    # External account identifier or username from that platform
    external_account_id = Column(String, nullable=True)

    # Tracks whether the platform is currently connected
    status = Column(String, default="connected", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
"""