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

    def main_generator(self, user_query: str, api_key: str, schema_info: str) -> Dict:
        """
        Generate a single SQL query based on user query and schema information.
        The query can be simple or complex depending on the user's needs.
        
        Args:
            user_query: Natural language query from user
            api_key: API key for LLM
            schema_info: Formatted schema string from user-uploaded file
        Returns:
            Dictionary containing:
                - user_query: Original user query
                - generated_sql: Single SQL query (no additional text/explanations)
        """
        # Use the provided schema_info directly
        initial_prompt = f"""Given these tables and columns (Schema):
{schema_info}

Generate a single SQL query for this request:
{user_query}

CRITICAL NOTE:
- Ensure that table and column names used in the SQL strictly match those defined in the schema, including preserving the original casing.
- Avoid referencing columns that do not exist in the corresponding table as defined in the schema.
- Ensure that column data types are properly considered when constructing SQL queries. Use consistent data types in logical comparisons to maintain accuracy and avoid type mismatches.
- Avoid using subqueries as expressions if they return more than one row
- Avoid using reserved SQL keywords as table/column aliases (e.g. 'is', 'as', 'by', 'on', 'in', 'to', 'for', 'from', 'where', 'select', 'group', 'order', 'having', 'join', 'left', 'right', 'inner', 'outer', 'cross', 'natural', 'using', 'with')
- Use descriptive and unique aliases that are not SQL keywords.
- If a table/column name is already short, consider using it without an alias.

Requirements:
- Return ONLY the raw SQL query text, no markdown formatting
- No explanations or additional text
- The query can be simple or complex depending on what's needed
- Use appropriate JOINs, subqueries, or aggregations if required
- Ensure the query is complete and executable"""
        generated_sql = generate_text(initial_prompt, api_key)
        generated_sql = self._clean_sql_output(generated_sql)
        return {
            "user_query": user_query,
            "generated_sql": generated_sql
        }