import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

DB_URL = settings.db_url
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine,autocommit=False,expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
