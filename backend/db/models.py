from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    linked_accounts = relationship("LinkedAccount", back_populates="user", cascade="all, delete")
    listings = relationship("Listing", back_populates="user")

# Connect External Resale Platforms (FR4)
# Side note: Using OAuth2.0 we can only access eBay and Depop. Graph API for Facebook.
# Mercari and Poshmark have no public API.
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


# FR5: Represents a resale listing shown on the dashboard
class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    condition = Column(String(255), nullable=False)
    platform = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    size = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    weight_lbs = Column(Float, nullable=True)
    image_url = Column(String(255), nullable=True)
    status = Column(String(255), default="active")

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="listings")


# Represents a user-submitted issue or problem report
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=True)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# FR4: Snapshot of a listing pulled from an external platform (eBay, etc.)
# Kept separate from the manual Listing model above so the dashboard isn't polluted.
class ListingSnapshot(Base):
    __tablename__ = "listing_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(255), nullable=False)
    platform_listing_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    quantity = Column(Integer, nullable=True)
    condition = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    item_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    captured_at = Column(DateTime, server_default=func.now())
