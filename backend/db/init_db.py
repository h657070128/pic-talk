# init_db.py
# Script to initialize database tables
import sys
from pathlib import Path

# Add parent directory to path so we can import db module
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from db.database import Base, engine
from db.image_practice_task import ImagePracticeTask
from db.user_practice_record import UserPracticeRecord

def init_db():
    """Create all database tables"""
    # Import all models so they're registered with Base
    # This ensures foreign key relationships are created correctly
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
