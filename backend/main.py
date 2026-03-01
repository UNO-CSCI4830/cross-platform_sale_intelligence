from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from backend.db.database import Base, engine, get_db
from backend.db.models import User, Issue, Listing
from backend.services.user_service import create_user, authenticate_user

Base.metadata.create_all(bind=engine) # Create tables

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
    return {"id": authenticated_user.id, "email": authenticated_user.email}

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

@app.get("/") # This is a decorator for HTML GET. Just "/" is the base page
def root():
    return {"Hello": "World"}


