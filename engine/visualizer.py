import os
import sys
from typing import Dict, List
import pandas as pd

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from llm_config.llm_call import generate_text

class SQLVisualizer:
    def __init__(self):
        pass

    def _clean_python_output(self, python_text: str) -> str:
        """
        Clean the Python output by removing any markdown code block markers.
        
        Args:
            python_text: The raw Python text that might contain markdown markers
            
        Returns:
            Cleaned Python text without any markdown markers
        """
        # Remove ```python and ``` markers if present
        python_text = python_text.replace('```python', '').replace('```', '')
        # Remove any leading/trailing whitespace
        return python_text.strip()
    
    def main_visualizer(self, query_info: str, query_results: List[Dict], api_key: str = None) -> Dict:
        try:
            # Create DataFrame just for reference
            df = pd.DataFrame(query_results)
            
            prompt = f"""
            Write Python code to create visualizations for this data.

            Query: {query_info}
            Available columns: {list(df.columns)}
            Data sample: {df.head().to_dict()}

            CRITICAL INSTRUCTIONS:
            - The variable 'execution_results' is already available and contains the data as a list of dictionaries.
            - DO NOT create or use any hardcoded or summary data.
            - Always start with: df = pd.DataFrame(execution_results)
            - Use only the 'df' DataFrame for all visualizations.
            - Do not create or use any other DataFrame or data variable.
            - Create visualizations using the DataFrame.
            - Use plt.figure() for each plot.
            - Use plt.show() to display plots.
            - Use plt.close() after each plot.
            - Handle multiple plots properly.
            - Return ONLY the raw Python code, no markdown formatting, no ```python or ``` markers.
            - Make sure plots are visible and well-formatted.
            """
            
            viz_code = generate_text(prompt, api_key)
            # Clean the visualization code to remove any markdown markers
            viz_code = self._clean_python_output(viz_code)

            return {
                "success": True,
                "generated_code": viz_code,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "generated_code": None,
                "error": str(e)
            }