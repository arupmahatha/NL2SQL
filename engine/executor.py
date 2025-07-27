from typing import Dict, List, Tuple
import re
from sqlalchemy import text

class SQLExecutor:
    def format_results_for_analysis(self, results: List[Dict]) -> str:
        """
        Format query results into clear, tabular text for LLM analysis
        Args:
            results: List of dictionaries containing query results
        Returns:
            Formatted string representation of results
        """
        if not results:
            return "No results found"

        # Get column names from first result
        columns = list(results[0].keys())
        
        # Calculate column widths
        col_widths = {col: len(col) for col in columns}
        for row in results:
            for col in columns:
                col_widths[col] = max(col_widths[col], len(str(row[col])))

        # Create header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        separator = "-" * len(header)

        # Format rows
        formatted_rows = []
        for row in results:
            formatted_row = " | ".join(str(row[col]).ljust(col_widths[col]) for col in columns)
            formatted_rows.append(formatted_row)

        # Combine all parts
        return "\n".join([header, separator] + formatted_rows)

    def is_read_only_query(self, query: str) -> bool:
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

    def main_executor(self, sql_query: str, engine) -> Tuple[bool, List[Dict], str, str]:
        """
        Validate and execute SQL query safely using the provided engine
        Returns:
            Tuple containing:
            - success: bool
            - results: List of dictionaries (row results)
            - formatted_results: Formatted string representation of results
            - error: Error message if any
        """
        try:
            # Validate query is read-only
            if not self.is_read_only_query(sql_query):
                return False, [], "", "Only SELECT queries are allowed for security reasons"
            
            # Execute the query directly using the provided engine
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                columns = result.keys()
                rows = result.fetchall()
                
            # Convert to list of dictionaries
            results = [dict(zip(columns, row)) for row in rows]
            formatted_results = self.format_results_for_analysis(results)
            return True, results, formatted_results, ""
        except Exception as e:
            return False, [], "", str(e) 