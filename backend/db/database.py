from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Use SQLite for local development.
# To switch to PostgreSQL for production, set DATABASE_URL in your .env file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# connect_args is SQLite-specific — safe to keep since the fallback above defaults to SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = Sessionlocal()  # Every HTTP request gets its own session
    try:
        yield db
    finally:
        db.close()  # Close session regardless of result