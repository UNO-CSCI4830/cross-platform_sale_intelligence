from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from urllib.parse import urlencode
import httpx

from backend.core.security import get_current_user, create_access_token
from backend.db.database import Base, engine, get_db
from backend.db.models import User, Issue, Listing, LinkedAccount
from backend.services.user_service import create_user, authenticate_user, update_email, change_password
from backend.services.platform_service import PLATFORM_CONFIGS, save_linked_account, get_valid_token

Base.metadata.create_all(bind=engine)  # Create tables if they do not already exist

app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic schemas ──────────────────────────────────────────────────────────
"""
IMPORTANT ABOUT VALIDATORS: FastAPI automatically catches these and returns 422.
It returns the message as a list of objects, so when writing test cases only
assert on the status code, not response.message.
"""

class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str

    @field_validator("email", "first_name", "last_name", "password")
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Account creation fields cannot be empty")
        return v


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email", "password")
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Login fields cannot be empty")
        return v


# FR14: User Profile Update
class UserUpdate(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Email field cannot be empty")
        return v


# FR3: Password Reset
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator("current_password", "new_password")
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Password fields cannot be empty")
        return v


class ListingCreate(BaseModel):
    user_id: int
    title: str
    price: float
    condition: str
    platform: str
    category: str | None = None
    size: str | None = None
    notes: str | None = None
    weight_lbs: float | None = None
    image_url: str | None = None
    status: str = "active"


class ListingResponse(BaseModel):
    id: int
    title: str
    price: float
    condition: str
    platform: str
    category: str | None = None
    size: str | None = None
    notes: str | None = None
    weight_lbs: float | None = None
    image_url: str | None = None
    status: str

    class Config:
        from_attributes = True


class IssueCreate(BaseModel):
    email: str | None = None
    message: str


class IssueOut(BaseModel):
    id: int
    email: str | None
    message: str
    created_at: str


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = create_user(user.email, user.first_name, user.last_name, user.password, db)
    # Return a token immediately so the frontend can log the user in right after signup
    token = create_access_token(created_user.id)
    return {
        "id": created_user.id,
        "email": created_user.email,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(user.email, user.password, db)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(authenticated_user.id)
    return {
        "id": authenticated_user.id,
        "email": authenticated_user.email,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Same format as /login but uses OAuth2 form format — for Swagger docs auth. TESTING ONLY."""
    authenticated_user = authenticate_user(form_data.username, form_data.password, db)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    tok = create_access_token(authenticated_user.id)
    return {"access_token": tok, "token_type": "bearer"}


@app.post("/logout")
async def logout():
    # Token deletion is handled client-side (localStorage). Nothing to do server-side.
    return {"message": "Logged out successfully"}


# FR14: Update a user's email
@app.put("/users/{user_id}")
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
):
    update_email(user_id=user_id, new_email=user_update.email, db=db)
    return {"message": "User profile updated successfully"}


# FR3: Update a user's password
@app.put("/users/{user_id}/password")
def change_user_password(
    user_id: int,
    password_update: PasswordUpdate,
    db: Session = Depends(get_db),
):
    change_password(
        user_id=user_id,
        current_password=password_update.current_password,
        new_password=password_update.new_password,
        db=db,
    )
    return {"message": "Password updated successfully"}


# ── Listing routes ────────────────────────────────────────────────────────────

# FR5: Unified Dashboard Display
@app.get("/listings/{user_id}", response_model=list[ListingResponse])
def get_user_listings(user_id: int, db: Session = Depends(get_db)):
    """Returns all active listings for a specific user."""
    return (
        db.query(Listing)
        .filter(Listing.user_id == user_id, Listing.status == "active")
        .all()
    )


@app.post("/listings", response_model=ListingResponse)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    """Create a new listing and save it to the database."""
    new_listing = Listing(
        user_id=listing.user_id,
        title=listing.title,
        price=listing.price,
        condition=listing.condition,
        platform=listing.platform,
        category=listing.category,
        size=listing.size,
        notes=listing.notes,
        weight_lbs=listing.weight_lbs,
        image_url=listing.image_url,
        status=listing.status,
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing


@app.put("/listings/{listing_id}", response_model=ListingResponse)
def update_listing(listing_id: int, listing: ListingCreate, db: Session = Depends(get_db)):
    """Update an existing listing."""
    db_listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db_listing.title = listing.title
    db_listing.price = listing.price
    db_listing.condition = listing.condition
    db_listing.platform = listing.platform
    db_listing.category = listing.category
    db_listing.size = listing.size
    db_listing.notes = listing.notes
    db_listing.weight_lbs = listing.weight_lbs
    db_listing.image_url = listing.image_url
    db_listing.status = listing.status
    db.commit()
    db.refresh(db_listing)
    return db_listing


@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    """Delete a listing."""
    db_listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(db_listing)
    db.commit()
    return {"message": "Listing deleted", "id": listing_id}


# ── Issue routes ──────────────────────────────────────────────────────────────

@app.post("/issues")
def report_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    new_issue = Issue(email=issue.email, message=issue.message)
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return {"status": "received", "issue_id": new_issue.id}


@app.get("/issues")
def list_issues(db: Session = Depends(get_db)):
    issues = db.query(Issue).order_by(Issue.id.desc()).all()
    return [
        {
            "id": i.id,
            "email": i.email,
            "message": i.message,
            "created_at": str(i.created_at),
        }
        for i in issues
    ]


# ── Platform OAuth routes ─────────────────────────────────────────────────────
# IMPORTANT: specific routes must come before wildcard routes.
# /auth/{platform}/status/{user_id} is registered before /auth/{platform}/callback
# so FastAPI doesn't match "status" as the `code` param in the callback route.

@app.get("/auth/{platform}/status/{user_id}")
def get_platform_status(platform: str, user_id: int, db: Session = Depends(get_db)):
    """FR4: Check if a platform account is linked for a given user."""
    account = db.query(LinkedAccount).filter_by(user_id=user_id, platform=platform).first()
    return {"linked": account is not None}


@app.get("/auth/{platform}/connect")
async def connect_platform(platform: str, current_user=Depends(get_current_user)):
    """FR4: Begin OAuth flow — returns the platform login URL as JSON for the frontend to redirect to."""
    if platform not in PLATFORM_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    params = {
        "client_id": PLATFORM_CONFIGS[platform]["client_id"],
        "redirect_uri": os.getenv("EBAY_RUNAME"),
        "response_type": "code",
        "scope": "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "state": str(current_user.id),
    }
    auth_url = PLATFORM_CONFIGS[platform]["auth_url"]
    # Return as JSON — the browser can't attach JWT headers on a plain redirect,
    # so the frontend reads auth_url and does window.location.href = data.auth_url
    return {"auth_url": f"{auth_url}?{urlencode(params)}"}


@app.get("/auth/{platform}/callback")
async def platform_callback(platform: str, code: str, state: str, db=Depends(get_db)):
    """FR4: Platform redirects here after user approves access. Exchanges code for tokens."""
    config = PLATFORM_CONFIGS[platform]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            config["token_url"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": os.getenv("EBAY_RUNAME"),
            },
            auth=(config["client_id"], config["client_secret"]),
        )
        tokens = response.json()

    print("eBay token response:", tokens)  # Temporary debug — remove after fixing

    await save_linked_account(user_id=int(state), platform=platform, tokens=tokens, db=db)

    return RedirectResponse(url=os.getenv("FRONTEND_URL", "http://localhost:3000"))


# ── eBay listings route ───────────────────────────────────────────────────────

@app.get("/ebay/listings/{user_id}")
async def get_ebay_listings(user_id: int, db: Session = Depends(get_db)):
    """FR4: Fetch the user's eBay inventory listings using their stored OAuth token."""
    try:
        token = await get_valid_token(user_id, "ebay", db)
    except HTTPException:
        raise HTTPException(status_code=404, detail="No linked eBay account found")

    api_base = PLATFORM_CONFIGS["ebay"]["api_base"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_base}/sell/inventory/v1/inventory_item",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            params={"limit": 50},
        )

    if response.status_code == 200:
        data = response.json()
        items = data.get("inventoryItems", [])
        return [_normalise_ebay_item(item) for item in items]
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"eBay API error: {response.text}",
        )


# FR12: Manual data refresh
@app.post("/listings/refresh")
async def refresh_listings(platform: str, current_user=Depends(get_current_user), db=Depends(get_db)):
    token = await get_valid_token(current_user.id, platform, db)
    # Refresh logic can be extended here per-platform
    return {"status": "listings refreshed"}


# ── Debug route (remove before production) ───────────────────────────────────

@app.post("/debug/create-test-listing")
async def create_test_listing(user_id: int, db: Session = Depends(get_db)):
    """Temporary: creates a test inventory item in eBay sandbox for the linked user."""
    token = await get_valid_token(user_id, "ebay", db)
    api_base = PLATFORM_CONFIGS["ebay"]["api_base"]

    test_item = {
        "availability": {"shipToLocationAvailability": {"quantity": 1}},
        "condition": "USED_EXCELLENT",
        "product": {
            "title": "Test Vintage Denim Jacket",
            "description": "A test listing created via API",
            "imageUrls": ["https://rebalancevintage.com/cdn/shop/files/Mar24-283199.jpg?v=1743522621"],
            "aspects": {"Size": ["M"], "Type": ["Outerwear"]},
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{api_base}/sell/inventory/v1/inventory_item/TEST-SKU-001",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Content-Language": "en-US",
            },
            json=test_item,
        )

    return {"status": response.status_code, "response": response.text}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalise_ebay_item(item: dict) -> dict:
    """Convert eBay inventory item shape to our listing shape."""
    product = item.get("product", {})
    aspects = product.get("aspects", {})
    return {
        "id":         item.get("sku", ""),
        "title":      product.get("title", "Untitled"),
        "price":      0,  # price lives on the offer, not the inventory item
        "condition":  item.get("condition", "Unknown"),
        "platform":   "eBay",
        "category":   aspects.get("Type", ["Other"])[0] if aspects.get("Type") else "Other",
        "size":       aspects.get("Size", [""])[0] if aspects.get("Size") else "",
        "notes":      product.get("description", ""),
        "status":     "active",
        "imageUrl":   product.get("imageUrls", [""])[0] if product.get("imageUrls") else "",
        "ebayItemId": item.get("sku", ""),
        "readOnly":   True,
    }