import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from typing import Dict, List, Tuple, Union
from llm_config.llm_call import generate_text

class SQLAnalyzer:
    def main_analyzer(self, query_info: str, query_results: List[Dict] = None, api_key: str = None) -> Dict[str, Union[bool, str, int, dict]]:
        """
        Analyze SQL query results or query intent and generate comprehensive insights
        
        Args:
            query_info: Original query information
            query_results: Optional list of dictionaries containing query results
            api_key: API key for LLM
        
        Returns:
            Dict containing:
            - success: bool
            - query_info: original query
            - record_count: number of records (if results provided)
            - analysis: LLM analysis response
            - error: error message if any
        """
        try:
            # Create analysis prompt
            if query_results:
                prompt = f"""
                Analyze the following data based on the query:
                "{query_info}"

                Data (list of records):
                {query_results}

                Provide a comprehensive analysis including:
                1. Key findings and patterns
                2. Notable relationships between metrics
                3. Important trends or anomalies
                4. Actionable insights and recommendations
                """
            else:
                prompt = f"""
                Analyze the following query and provide insights:
                "{query_info}"

                Provide a comprehensive analysis including:
                1. Query intent and objectives
                2. Key information requirements
                3. Potential data points of interest
                4. Suggested approach for data retrieval
                """
            
            # Get analysis from LLM
            analysis = generate_text(prompt, api_key)
            
            return {
                "success": True,
                "query_info": query_info,
                "record_count": len(query_results) if query_results else 0,
                "analysis": analysis,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "query_info": query_info,
                "record_count": 0,
                "analysis": None,
                "error": str(e)
            }