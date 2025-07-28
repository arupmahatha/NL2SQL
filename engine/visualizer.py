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
        """
        Generate visualization code for the given query and results using LLM.
        Args:
            query_info: The original query string
            query_results: List of dictionaries with SQL results
            api_key: API key for LLM (optional, will use .env if not provided)
        Returns:
            Dict with keys: success, generated_code, error
        """
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
            - Use plt.figure(figsize=(12, 8), dpi=300) for each plot for high quality.
            - DO NOT use plt.show() or plt.close() - these will be handled automatically.
            - Handle multiple plots properly.
            - Return ONLY the raw Python code, no markdown formatting, no ```python or ``` markers.
            - Make sure plots are visible and well-formatted with good quality.
            - Each plot should be a separate plt.figure() call.
            - Use clear titles, labels, and readable fonts.
            - Set appropriate figure sizes for readability.
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