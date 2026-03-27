import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:omarsaad1@localhost:5432/aipm_boss"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from models.user import User
    from models.project import Project
    from models.task import Task
    from models.sprint import Sprint
    from models.developer import Developer
    Base.metadata.create_all(bind=engine)
    print("[Database] All tables created successfully")


def check_connection():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("[Database] Connection successful")
        return True
    except Exception as e:
        print(f"[Database] Connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("[Database] Checking connection...")
    check_connection()
    print("[Database] Creating tables...")
    create_tables()