import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
db_url = "postgresql://postgres:12345678@localhost:5432/db"
DB_URL = os.getenv("DB_URL")
engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine,autocommit=False,expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


