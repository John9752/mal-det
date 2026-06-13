from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from pathlib import Path

# Get database path from environment or default to local file
database_env = os.getenv("DATABASE_PATH", "./malnutrition.db")
db_path = Path(database_env).resolve()

# Critical: Ensure the directory exists (especially for Render /data mounts)
db_path.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_path}"
print(f"DATABASE_URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
