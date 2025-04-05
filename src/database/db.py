import os
import time
from urllib.parse import urlparse
from peewee import PostgresqlDatabase
from playhouse.pool import PooledPostgresqlDatabase

# Try to get database config from individual environment variables first
db_name = os.getenv('DB_NAME', 'networker')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', '5432'))

# If DATABASE_URL is set, override the individual settings
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Handle Heroku's postgres:// vs postgresql:// issue
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    
    # Parse database URL
    url = urlparse(database_url)
    db_name = url.path[1:]
    db_user = url.username
    db_password = url.password
    db_host = url.hostname
    db_port = url.port or 5432

# Set up database configuration
db_config = {
    'database': db_name,
    'user': db_user,
    'password': db_password,
    'host': db_host,
    'port': db_port,
}

# Enable SSL in production (Heroku requires this)
if os.getenv('ENVIRONMENT') == 'production' or 'herokuapp.com' in db_host:
    db_config['sslmode'] = 'require'

# Use connection pooling in production
is_production = os.getenv('ENVIRONMENT') == 'production' or 'herokuapp.com' in db_host
if is_production:
    db = PooledPostgresqlDatabase(
        db_name,
        max_connections=32,
        stale_timeout=300,
        **db_config
    )
else:
    # Standard connection for local development
    db = PostgresqlDatabase(**db_config)

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
    from src.database.models import BaseModel
    
    # Get all model classes that inherit from BaseModel
    models = BaseModel.__subclasses__()
    
    # Try to connect with retries
    for attempt in range(3):
        if connect_db():
            break
        print(f"Retrying connection, attempt {attempt+1}/3")
        time.sleep(1)
    else:
        print("Failed to connect to database after 3 attempts")
        return None
    
    # Create tables
    db.create_tables(models, safe=True)
    print(f"Database initialized successfully at {db_host}:{db_port}/{db_name}")
    
    return db 