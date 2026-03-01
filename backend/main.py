from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from backend.db.database import Base, engine, get_db
from backend.db.models import User
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

@app.get("/") # This is a decorator for HTML GET. Just "/" is the base page
def root():
    return {"Hello": "World"}


