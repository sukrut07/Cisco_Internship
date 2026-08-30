import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

default_db = "sqlite:///./netsage.db"
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    tmp_db_path = os.path.join(tempfile.gettempdir(), "netsage.db")
    default_db = f"sqlite:///{tmp_db_path}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default_db)

# SQLite needs connect_args check_same_thread=False
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
