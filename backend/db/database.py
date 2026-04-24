from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = Sessionlocal()  # Every HTTP request gets its own session
    try:
        yield db
    finally:
        db.close()  # Close session regardless of result