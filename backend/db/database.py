from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" #SQLite file on local machine, if it doesn't exist it will be created.

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Sessionlocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()