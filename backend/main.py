from dotenv import load_dotenv
import os

load_dotenv() #Load environment variables

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.core.security import get_current_user, create_access_token
from backend.db.database import Base, engine, get_db
from backend.db.models import User, Issue, Listing
from backend.services.user_service import create_user, authenticate_user
from backend.services.platform_service import PLATFORM_CONFIGS, save_linked_account
import httpx



Base.metadata.create_all(bind=engine) # Create tables, if they do not already exist

# FastAPI app instance
app = FastAPI()

app.add_middleware( 
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Allows front end and backend to host locally, will be changed later when we find where we are hostings.

#Pydantic schemas
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email:str
    password: str

# FR14: User Profile Update input model
class UserUpdate(BaseModel):
    email: str  # New email address for the user

# Data returned to the dashboard for each listing
class ListingResponse(BaseModel):
    id: int
    title: str
    price: int
    condition: str
    platform: str
    status: str

    class Config:
        from_attributes = True

# FR4: Input model for connecting an external platform
class PlatformConnectRequest(BaseModel):
    user_id: int
    platform_name: str
    external_account_id: str | None = None


# FR4: Input model for disconnecting an external platform
class PlatformDisconnectRequest(BaseModel):
    user_id: int
    platform_name: str


# FR4: Response model for connected platform data
class PlatformConnectionOut(BaseModel):
    id: int
    user_id: int
    platform_name: str
    external_account_id: str | None
    status: str

    class Config:
        from_attributes = True

# Schema for submitting a new issue report
class IssueCreate(BaseModel):
    email: str | None = None  # Optional contact email
    message: str              # Description of the issue


# Schema for returning issue data
class IssueOut(BaseModel):
    id: int
    email: str | None
    message: str
    created_at: str

#Route for signing up
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user: #If this user already exists
        raise HTTPException(status_code = 400, detail = "Email already registered")
    created_user = create_user(user.email, user.password, db)
    return {"id": created_user.id, "email": created_user.email}

#Route for logging in
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(user.email, user.password, db) #authenticate_user returns the user, returns the user object
    if not authenticated_user: #user fails to login, authenticate_user returns None, making this if statement true and returns an error
        raise HTTPException(status_code = 400, detail = "Invalid credentials")
    token = create_access_token(authenticated_user.id)
    return{
            "id": authenticated_user.id,
            "email": authenticated_user.email,
            "access_token": token,
            "token_type": "bearer"
        }

@app.put("/users/{user_id}")
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    FR14: Allows a user to update their profile information (email).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = user_update.email  # Update email
    db.commit()
    db.refresh(user)

    return {"message": "User profile updated successfully"}

# FR5: Unified Dashboard Display
@app.get("/listings/{user_id}", response_model=list[ListingResponse])
def get_user_listings(user_id: int, db: Session = Depends(get_db)):
    """
    Returns all active listings for a specific user
    """
    listings = (
        db.query(Listing)
        .filter(Listing.user_id == user_id, Listing.status == "active")
        .all()
    )

    return listings

@app.post("/issues")
def report_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    # Create a new Issue object from user input
    new_issue = Issue(
        email=issue.email,
        message=issue.message
    )

    # Save the issue to the database
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    # Confirm successful submission
    return {
        "status": "received",
        "issue_id": new_issue.id
    }

@app.get("/issues")
def list_issues(db: Session = Depends(get_db)):
    # Retrieve all reported issues, newest first
    issues = db.query(Issue).order_by(Issue.id.desc()).all()

    # Format issue data for response
    return [
        {
            "id": i.id,
            "email": i.email,
            "message": i.message,
            "created_at": str(i.created_at),
        }
        for i in issues
    ]

# Connect External Resale Platforms (FR4)
@app.get("/auth/{platform}/connect")
async def connect_platform(platform: str, current_user=Depends(get_current_user)):
    params = {
        "client_id": PLATFORM_CONFIGS[platform]["client_id"],
        "redirect_uri": f"{os.getenv('REDIRECT_BASE_URL')}/auth/{platform}/callback", #IMPORTANT: This exact url must be registered with the service and then updated when hosting
        "response_type": "code",
        "scope": "https://api.ebay.com/oauth/api_scope/sell.inventory", #Tells ebay we want to access listings
        "state": current_user.id  # pass user ID so we know who to link on callback
    }
    auth_url = PLATFORM_CONFIGS[platform]["auth_url"]
    return RedirectResponse(url=f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}") #builds the url using the parameters above, also where the user is sent to login

@app.get("/auth/{platform}/callback")
async def platform_callback(platform: str, code: str, state: str, db=Depends(get_db)):
    config = PLATFORM_CONFIGS[platform]
    
    # Exchange the code eBay gave us for actual tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config["token_url"], #Server call
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{os.getenv('REDIRECT_BASE_URL')}/auth/{platform}/callback",
            },
            auth=(config["client_id"], config["client_secret"])
        )
        tokens = response.json()
    
    # Save tokens to DB
    await save_linked_account(
        user_id=int(state),
        platform=platform,
        tokens=tokens,
        db=db
    )
    
    return {"status": "linked"}
# FR4: Connect an external resale platform to a user account
"""
@app.post("/platforms/connect")
def connect_platform(
    connection: PlatformConnectRequest,
    db: Session = Depends(get_db)
):
    # Check that the user exists in our system
    user = db.query(User).filter(User.id == connection.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent duplicate active connections for the same platform
    existing = (
        db.query(PlatformConnection)
        .filter(
            PlatformConnection.user_id == connection.user_id,
            PlatformConnection.platform_name == connection.platform_name,
            PlatformConnection.status == "connected"
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Platform already connected")

    new_connection = PlatformConnection(
        user_id=connection.user_id,
        platform_name=connection.platform_name,
        external_account_id=connection.external_account_id,
        status="connected"
    )

    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)

    return {"message": "Platform connected successfully", "connection_id": new_connection.id}


# FR4: Get all connected platforms for a user
@app.get("/platforms/{user_id}", response_model=list[PlatformConnectionOut])
def get_connected_platforms(user_id: int, db: Session = Depends(get_db)):
    connections = (
        db.query(PlatformConnection)
        .filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.status == "connected"
        )
        .all()
    )

    return connections


# FR4: Disconnect a platform from a user account
@app.delete("/platforms/disconnect")
def disconnect_platform(
    request: PlatformDisconnectRequest,
    db: Session = Depends(get_db)
):
    connection = (
        db.query(PlatformConnection)
        .filter(
            PlatformConnection.user_id == request.user_id,
            PlatformConnection.platform_name == request.platform_name,
            PlatformConnection.status == "connected"
        )
        .first()
    )

    if not connection:
        raise HTTPException(status_code=404, detail="Connected platform not found")

    connection.status = "disconnected"
    db.commit()

    return {"message": "Platform disconnected successfully"}
"""
# Temporary test data for dashboard development
@app.get("/test/add-listing")
def add_test_listing(db: Session = Depends(get_db)):
    listing = Listing(
        user_id=1,
        title="Nike Tech Fleece Set",
        price=120,
        condition="Excellent",
        platform="Depop"
    )
    db.add(listing)
    db.commit()
    return {"message": "Test listing added"}



