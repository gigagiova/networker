import os
import time
from peewee import PostgresqlDatabase
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# --- Simplified Local Development Config ---
# Force using variables from .env or these defaults
db_name = os.getenv('DB_NAME', 'networker')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', '5433'))

print(f"--- Connecting to: {db_host}:{db_port}/{db_name} as {db_user} ---")

# Directly initialize the database connection
db = PostgresqlDatabase(
    db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
# --- End Simplified Config ---

def connect_db():
    """Connect to the database with retry logic"""
    try:
        db.connect(reuse_if_open=True)
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def init_db():
    """Initialize the database and create tables if they don't exist"""
    from src.database.models.base import BaseModel
    from src.database.models.candidate import Candidate
    
    models = BaseModel.__subclasses__()
    if not models:
        models = [Candidate] 

    for attempt in range(3):
        if connect_db():
            break
        print(f"Retrying connection, attempt {attempt+1}/3")
        time.sleep(1)
    else:
        print("Failed to connect to database after 3 attempts")
        return None
    
    try:
        db.create_tables(models, safe=True)
        print(f"Database initialized successfully at {db_host}:{db_port}/{db_name}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return None

    return db 