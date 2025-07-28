from sqlalchemy import create_engine

def get_engine_from_path(db_path: str):
    """Create a SQLAlchemy engine from a SQLite file path."""
    return create_engine(f"sqlite:///{db_path}") 