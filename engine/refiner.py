import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from typing import Dict, List
from llm_config.llm_call import generate_text

class SQLRefiner:

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
    
    def main_refiner(self, sql_query: str, value_mappings: List[Dict]) -> Dict:
        """
        Refine SQL query with provided value mappings.
        
        Args:
            sql_query: SQL query to refine
            value_mappings: List of dictionaries containing original and matched values
            
        Returns:
            Dictionary containing:
                - original_sql: Input SQL query
                - value_mappings: List of matched values with scores
                - refined_sql: Refined or original SQL query
        """
        # If no value mappings provided, return original query
        if not value_mappings:
            return {
                "original_sql": sql_query,
                "value_mappings": [],
                "refined_sql": sql_query
            }

        # Filter out mappings with score 100
        filtered_mappings = [mapping for mapping in value_mappings if mapping.get("score", 0) != 100]
        
        # If no mappings remain after filtering, return original query
        if not filtered_mappings:
            return {
                "original_sql": sql_query,
                "value_mappings": value_mappings,
                "refined_sql": sql_query
            }

        # Refine SQL with filtered mappings
        refinement_prompt = f"""Return ONLY the modified SQL query with these replacements:
{chr(10).join(f"{m['original_value']} -> {m['matched_value']}" for m in filtered_mappings)}
Query: {sql_query}"""
        
        refined_sql = generate_text(refinement_prompt)
        # Clean the refined SQL to remove any markdown markers
        refined_sql = self._clean_sql_output(refined_sql)

        # Return results
        return {
            "original_sql": sql_query,
            "value_mappings": value_mappings,
            "refined_sql": refined_sql
        }