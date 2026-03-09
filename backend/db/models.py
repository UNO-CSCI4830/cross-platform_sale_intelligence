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

# FR4: Stores external resale platforms linked to a user account
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
