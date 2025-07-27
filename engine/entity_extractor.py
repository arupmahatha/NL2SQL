import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from typing import Dict, List
from llm_config.llm_call import generate_text

class EntityExtractor:
    def main_entity_extractor(self, sql_query: str, api_key: str) -> List[Dict]:
        """
        Extract entities from SQL query
        Args:
            sql_query: SQL query to analyze
            api_key: API key for LLM
        Returns:
            List of dictionaries containing table, column, value mappings
        """
        # Get entity mapping from LLM
        extraction_prompt = f"""You are an SQL entity extractor. Your ONLY task is to extract real-world entities.

Format: table_name|column_name|comparison_value

Step 1 - SQL Structure Analysis:
1. First identify the actual database tables (not views/CTEs):
   - CTEs (WITH clause) are temporary views, NEVER use them as table names
   - Subqueries are temporary views, NEVER use them as table names
   - Table aliases (e.g., 'p', 't1') are shortcuts, NEVER use them as table names

2. For each column, trace its true origin:
   - Follow the JOIN chain to find the source table
   - Resolve aliases to full table names (e.g., 'p.name' comes from 'Program.name')
   - Identify computed columns (they are not real data)

Step 2 - Entity Identification:
ONLY extract entities that meet ALL these criteria:
1. Table name must be:
   - An actual database table (not a CTE, view, or alias)
   - The original source table (not an intermediate join)

2. Column must be:
   - A real data column (not computed/derived)
   - From the source table (not aggregated or transformed)
   - Storing actual entity data (names, descriptions, IDs, etc.)
   - MUST be in a WHERE clause condition (NOT in SELECT clause)

3. Comparison value must be:
   - An actual specific value being compared
   - Not NULL
   - Not a mathematical comparison (>, <, >=, <=)
   - Not a logical condition (AND, OR, NOT)
   - Not a pattern match (LIKE, IN)
   - Not a date (e.g., '2025-01-01')
   - Can be any specific value including numbers

NEVER output any of these:
- NULL values in any field
- CTE names as table names (e.g., 'ProgramMetrics')
- Table aliases as table names (e.g., 'p' instead of 'Program')
- Computed/derived columns
- Aggregated fields (COUNT, SUM, AVG, etc.)
- Mathematical comparisons
- Columns without specific value comparisons
- Columns that only appear in SELECT clause (not in WHERE)

Example Valid Extractions:
- Program|name|John Smith              # Real table, real column, specific value in WHERE
- Student|email|alice@example.com      # Real table, real column, specific value in WHERE
- district|id|30                       # Real table, numeric column, specific value in WHERE

Example Invalid Extractions (NEVER output these):
- pm|count|5                           # Uses CTE as table
- p|name|NULL                          # Uses alias and NULL
- Program|enrolled_learners|>0         # Mathematical comparison
- Program|avg_completion_time|3.5      # Computed column
- course|date|2025-01-01               # Date comparison

CRITICAL INSTRUCTIONS:
- If no valid entities are found, return ABSOLUTELY NOTHING. Not even empty lines or explanations.
- ONLY output the exact table_name|column_name|comparison_value format for valid entities.
- ANY other output format is considered an error.
- If no entities are found, return an empty string, not an error message.
"""
        try:
            entity_text = generate_text(f"{extraction_prompt}\n\nQuery: {sql_query}", api_key)
            
            # Check if the response contains error messages or explanations
            if any(error_word in entity_text.lower() for error_word in ['error', 'no entities', 'not found', 'invalid', 'cannot']):
                return []
            
            # Parse and validate extracted entities
            extracted_entities = []
            for line in entity_text.strip().split('\n'):
                if '|' not in line or line.strip() == '':
                    continue
                try:
                    parts = line.strip().split('|')
                    if len(parts) == 3:
                        table, column, value = parts
                        table = table.strip()
                        column = column.strip()
                        value = value.strip()
                        
                        # Validate that we have actual values
                        if table and column and value:
                            extracted_entities.append({
                                "table": table,
                                "column": column,
                                "value": value
                            })
                except Exception:
                    # Skip malformed lines
                    continue
                    
            return extracted_entities
        except Exception as e:
            # If there's any error, return empty list
            return [] 