from dotenv import load_dotenv
import os

load_dotenv() #Load environment variables

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from backend.core.security import get_current_user, create_access_token
from backend.db.database import Base, engine, get_db
from backend.db.models import User, Issue, ListingSnapshot
from backend.services.user_service import create_user, authenticate_user,update_email, change_password
from backend.services.platform_service import PLATFORM_CONFIGS, save_linked_account, fetch_and_save_listings
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
"""
IMPORTANT ABOUT VALIDATORS: FastAPI automatically catches these and returns 422, HOWEVER it returns the message as a list of objects
So when making test cases only assert for the status code, not the response.message
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
    email:str
    password: str

    @field_validator("email", "password") #password is sort of redunant here due to the previous class validator
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Login fields cannot be empty")
        return v

# FR14: User Profile Update input model
class UserUpdate(BaseModel):
    email: str  # New email address for the user

    @field_validator("email")
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Email field cannot be empty")
        return v

# FR3: Password Reset
class PasswordUpdate(BaseModel):
    current_password: str 
    new_password:str 

    @field_validator("current_password", "new_password")
    @classmethod
    def fields_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Password fields cannot be empty")
        return v

# Data returned to the dashboard for each listing
class ListingResponse(BaseModel):
    id: int
    title: str
    price: float
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
    created_user = create_user(user.email,user.first_name, user.last_name, user.password, db)
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

@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Same format as /login, just uses a different format for swagger docs authorization. TESTING ONLY
    """
    authenticated_user = authenticate_user(form_data.username, form_data.password, db)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(authenticated_user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/logout")
async def logout():
    return {"message": "Logged out sucessfully"} #Option 1 delete token stored on user's browser, which is done from frontend.


@app.put("/users/{user_id}")
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    FR14: Allows a user to update their profile information (email).
    """
    update_email(user_id = user_id, new_email = user_update.email, db = db)

    return {"message": "User profile updated successfully"}

@app.put("/users/{user_id}/password")
def change_user_password(
    user_id: int,
    password_update: PasswordUpdate,
    db: Session = Depends(get_db)
):
    """
    FR2: Allows a user to change their password
    """
    change_password(user_id = user_id, current_password = password_update.current_password, new_password = password_update.new_password, db = db)
    return {"message": "Password updated successfully"}

# FR5: Unified Dashboard Display
@app.get("/listings/{user_id}", response_model=list[ListingResponse])
def get_user_listings(user_id: int, db: Session = Depends(get_db)):
    """
    Returns all active listings for a specific user
    """
    listings = (
        db.query(ListingSnapshot)
        .filter(ListingSnapshot.user_id == user_id, ListingSnapshot.status == "active")
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
async def connect_platform(platform: str, current_user = Depends(get_current_user)  ): 
    params = {
        "client_id": PLATFORM_CONFIGS[platform]["client_id"],
        "redirect_uri": f"{os.getenv('REDIRECT_BASE_URL')}/auth/{platform}/callback", #IMPORTANT: This exact url must be registered with the service and then updated when hosting
        "response_type": "code",
        "scope": PLATFORM_CONFIGS[platform]["scope"], #pulled from configs
        "state": current_user,  # pass user ID so we know who to link on callback, ***Swap with current_user.id when frontend integration is ready***
        "prompt": "login"
    }
    auth_url = PLATFORM_CONFIGS[platform]["auth_url"]
    return RedirectResponse(url=f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}") #builds the url using the parameters above, also where the user is sent to login

@app.get("/auth/{platform}/callback")
async def platform_callback(platform: str, code: str, state: str, db = Depends(get_db)):
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
    
    # Save tokens to db
    await save_linked_account(
        user_id=int(state),
        platform=platform,
        tokens=tokens,
        db=db
    )
    # Get initial listings at time of linking and save to db 
    await fetch_and_save_listings(int(state), platform, db) #state is the same as user.id
    
    return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}/Dashboard")

#FR 12 manual data refresh
@app.post("listings/refresh")
async def refresh_listings(platform: str, current_user = Depends(get_current_user), db = Depends(get_db)):
    await fetch_and_save_listings(current_user, platform, db)
    return {"status": "listings refreshed"}





