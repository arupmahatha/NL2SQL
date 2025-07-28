import os
import tempfile
import pandas as pd
from sqlalchemy import create_engine, inspect
from utils.db_utils import get_engine_from_path

class SchemaEngine:
    @staticmethod
    def from_upload(db_file):
        suffix = db_file.name.split('.')[-1].lower()
        if suffix in ["db", "sqlite", "sqlite3"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{suffix}') as tmp_file:
                tmp_file.write(db_file.read())
                tmp_path = tmp_file.name
            engine = create_engine(f"sqlite:///{tmp_path}")
            schema_info = SchemaEngine._extract_schema_from_engine(engine)
            return engine, schema_info
        elif suffix in ["csv"]:
            uploaded_df = pd.read_csv(db_file)
            engine = create_engine("sqlite:///:memory:")
            uploaded_df.to_sql("uploaded_table", engine, index=False, if_exists="replace")
            schema_info = SchemaEngine._extract_schema_from_dataframe(uploaded_df, "uploaded_table")
            return engine, schema_info
        elif suffix in ["xlsx", "xls"]:
            uploaded_df = pd.read_excel(db_file)
            engine = create_engine("sqlite:///:memory:")
            uploaded_df.to_sql("uploaded_table", engine, index=False, if_exists="replace")
            schema_info = SchemaEngine._extract_schema_from_dataframe(uploaded_df, "uploaded_table")
            return engine, schema_info
        else:
            raise ValueError("Unsupported file type. Please upload SQLite, CSV, or Excel.")

    @staticmethod
    def from_path(db_path):
        engine = get_engine_from_path(db_path)
        schema_info = SchemaEngine._extract_schema_from_engine(engine)
        return engine, schema_info

    @staticmethod
    def _extract_schema_from_engine(engine):
        inspector = inspect(engine)
        formatted_schema = []
        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                col_info = f"{col['name']} ({col['type']})"
                columns.append(col_info)
            formatted_schema.append(f"Table: {table_name}\nColumns:\n" + "\n".join(f"  - {col}" for col in columns))
        return "\n\n".join(formatted_schema)

    @staticmethod
    def _extract_schema_from_dataframe(df, table_name):
        columns = [f"{col} ({str(dtype)})" for col, dtype in df.dtypes.items()]
        return f"Table: {table_name}\nColumns:\n" + "\n".join(f"  - {col}" for col in columns) 