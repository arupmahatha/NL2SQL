from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from urllib.parse import quote_plus
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'client': os.getenv('DB_CLIENT', 'postgres'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Validate required environment variables
required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Create SQLAlchemy engine with read-only mode
# URL encode the password to handle special characters
encoded_password = quote_plus(DB_CONFIG['password'])
DATABASE_URL = f"postgresql://{DB_CONFIG['username']}:{encoded_password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Create engine with read-only mode
engine = create_engine(
    DATABASE_URL,
    connect_args={'options': '-c default_transaction_read_only=on'}
)

# Create session factory with read-only mode
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()

def is_read_only_query(query):
    """
    Check if the query is read-only by ensuring no blocked commands appear as complete words
    """
    query = query.lstrip().lower()
    blocked_commands = [
        'insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate',
        'grant', 'revoke', 'commit', 'rollback'
    ]
    
    # First check if query starts with a blocked command
    first_word = query.split()[0] if query else ""
    if first_word in blocked_commands:
        return False
        
    # Then check if any blocked command appears as a complete word in the query
    for cmd in blocked_commands:
        # \b matches word boundaries, ensuring we match complete words only
        if re.search(r'\b' + cmd + r'\b', query):
            return False
            
    return True

def get_db():
    """
    Get database session (read-only)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_query_pandas(query, params=None, engine=None):
    """
    Execute a query and return results as pandas DataFrame (read-only)
    """
    if not is_read_only_query(query):
        raise ValueError("Only SELECT queries are allowed for security reasons")
    import pandas as pd
    use_engine = engine if engine is not None else globals()['engine']
    return pd.read_sql_query(text(query), use_engine, params=params)

def execute_query_with_columns(query, params=None, engine=None):
    """
    Execute a raw SQL query and return (columns, rows) (read-only)
    """
    if not is_read_only_query(query):
        raise ValueError("Only SELECT queries are allowed for security reasons")
    use_engine = engine if engine is not None else globals()['engine']
    with use_engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        columns = result.keys()
        rows = result.fetchall()
        return columns, rows 