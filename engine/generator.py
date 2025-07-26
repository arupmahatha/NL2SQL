import os
import sys
import json
from typing import Dict

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from llm_config.llm_call import generate_text

class SQLGenerator:
    def __init__(self):
        pass

    def _clean_sql_output(self, sql_text: str) -> str:
        """
        Clean the SQL output by removing any markdown code block markers.
        
        Args:
            sql_text: The raw SQL text that might contain markdown markers
            
        Returns:
            Cleaned SQL text without any markdown markers
        """
        # Remove ```sql and ``` markers if present
        sql_text = sql_text.replace('```sql', '').replace('```', '')
        # Remove any leading/trailing whitespace
        return sql_text.strip()

    def _format_schema_info(self) -> str:
        """
        Read and format the database schema information from db_schema.json
        
        Returns:
            Formatted string containing table and column information with detailed metadata
        """
        schema_path = os.path.join(project_root, 'utils', 'db_schema.json')
        with open(schema_path, 'r') as f:
            schema_data = json.load(f)
        
        formatted_schema = []
        for table in schema_data['db_schema']:
            table_name = table['table_name']
            columns = []
            for col in table['columns']:
                # Format column information with type, nullable status, and default value
                col_info = f"{col['name']} ({col['type']})"
                columns.append(col_info)
            
            formatted_schema.append(f"Table: {table_name}\nColumns:\n" + "\n".join(f"  - {col}" for col in columns))
        
        return "\n\n".join(formatted_schema)

    def main_generator(self, user_query: str) -> Dict:
        """
        Generate a single SQL query based on user query and schema information.
        The query can be simple or complex depending on the user's needs.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary containing:
                - user_query: Original user query
                - generated_sql: Single SQL query (no additional text/explanations)
        """
        # Get formatted schema information
        formatted_metadata = self._format_schema_info()
        print("\nSchema:\n",formatted_metadata)
        
        # Read guidance information
        guidance_path = os.path.join(project_root, 'utils', 'guidance.txt')
        with open(guidance_path, 'r') as f:
            guidance_info = f.read()
        
        # Generate SQL
        initial_prompt = f"""Given these tables and columns (Schema):
{formatted_metadata}

Guidance:
{guidance_info}

Generate a single SQL query for this request:
{user_query}

CRITICAL NOTE:
- Ensure that table and column names used in the SQL strictly match those defined in the schema, including preserving the original casing.
- Avoid referencing columns that do not exist in the corresponding table as defined in the schema. For instance, if poims_user_id is not a column in the survey table, do not use expressions like survey.poims_user_id.
- Ensure that column data types are properly considered when constructing SQL queries. Use consistent data types in logical comparisons to maintain accuracy and avoid type mismatches for example, never compare an integer directly with a character varying.
- Avoid using subqueries as expressions if they return more than one row
- Avoid using reserved SQL keywords as table/column aliases (e.g. 'is', 'as', 'by', 'on', 'in', 'to', 'for', 'from', 'where', 'select', 'group', 'order', 'having', 'join', 'left', 'right', 'inner', 'outer', 'cross', 'natural', 'using', 'with')
- Use descriptive and unique aliases that are not SQL keywords (e.g. use 'insp_sch' instead of 'is', 'fp_shop' instead of 'fps')
- If a table/column name is already short, consider using it without an alias
- Use the guidance if found relevant or helpful for the specific case.

Requirements:
- Return ONLY the raw SQL query text, no markdown formatting
- No explanations or additional text
- The query can be simple or complex depending on what's needed
- Use appropriate JOINs, subqueries, or aggregations if required
- Ensure the query is complete and executable"""
        
        generated_sql = generate_text(initial_prompt)
        # Clean the generated SQL to remove any markdown markers
        generated_sql = self._clean_sql_output(generated_sql)

        # Return results
        return {
            "user_query": user_query,
            "generated_sql": generated_sql
        }