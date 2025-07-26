# SQL Generation and Analysis System

A sophisticated system that leverages Large Language Models (LLMs) to generate, refine, and analyze SQL queries from natural language input. The system supports either DeepSeek or Gemini model for high-quality SQL generation and validation.

## System Architecture

The system is built with a modular architecture consisting of several key components:

### 1. LLM Configuration (`llm_config/`)
- Manages interactions with LLM providers (supports DeepSeek or Gemini)
- Handles API calls, conversation history, and response formatting
- Configurable model selection and parameters
- Maintains conversation context for improved response quality

### 2. Core Engine Components (`engine/`)

#### SQL Generator
- Converts natural language queries into SQL using LLMs
- Integrates schema information for context-aware generation
- Supports complex queries with JOINs, subqueries, and aggregations
- Ensures SQL syntax correctness and completeness
- Maintains strict schema compliance and naming conventions

#### Entity Extractor
- Analyzes generated SQL to identify real-world entities
- Extracts table, column, and value mappings
- Filters out computed columns, aliases, and invalid entities
- Maintains strict validation rules for entity extraction

#### Value Matcher
- Matches extracted entities against database values
- Validates entity existence and relationships
- Ensures data consistency and accuracy

#### SQL Refiner
- Refines generated SQL based on entity matching results
- Optimizes query structure and performance
- Ensures query correctness and efficiency

#### SQL Executor
- Executes refined SQL queries against the database
- Handles query execution and result retrieval
- Manages database connections and transactions
- Provides formatted results for analysis

#### Result Analyzer
- Analyzes query execution results
- Provides insights and explanations
- Generates human-readable summaries

#### SQL Visualizer
- Generates Python visualization code for query results
- Uses LLM to create appropriate visualizations based on data
- Supports various chart types and data representations
- Ensures clean and reusable visualization code

### 3. Utilities (`utils/`)
- Database Configuration: Manages database connections and configurations
- Search Utilities: Provides fuzzy search and matching capabilities
- Schema Files: Contains database schema definitions in JSON format
- Guidance: Contains system prompts and guidance for LLM interactions

## Setup and Configuration

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **API Keys**
   Set one of the following environment variables based on your chosen LLM:
   - `DEEPSEEK_API_KEY` (for DeepSeek model)
   - `GEMINI_API_KEY` (for Gemini model)

3. **Database Configuration**
   Configure the following environment variables for database connection:
   - `DB_HOST`: Database host address
   - `DB_PORT`: Database port (default: 5432)
   - `DB_NAME`: Database name
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password

## Example Usage

The system includes example scripts demonstrating the usage of each component:
- `engine/*_test.py`: Example scripts for core engine components
- `utils/*_test.py`: Example scripts for utility functions
- `llm_config/llm_call_test.py`: Example script for LLM configuration

Run example scripts using:
```bash
python engine/generator_test.py  # Example of using the SQL generator
python engine/entity_extractor_test.py  # Example of using the entity extractor
python engine/value_matcher_test.py  # Example of using the value matcher
python engine/refiner_test.py  # Example of using the SQL refiner
python engine/executor_test.py  # Example of using the SQL executor
python engine/analyzer_test.py  # Example of using the result analyzer
python engine/visualizer_test.py  # Example of using the SQL visualizer
```

## Project Structure

```
.
├── engine/                 # Core SQL generation and processing engine
│   ├── generator.py       # SQL query generation
│   ├── entity_extractor.py # Entity extraction from SQL
│   ├── value_matcher.py   # Value matching utilities
│   ├── refiner.py        # SQL query refinement
│   ├── executor.py       # SQL query execution
│   ├── analyzer.py       # Result analysis
│   ├── visualizer.py     # Query result visualization
│   └── *_test.py         # Example usage scripts
├── llm_config/           # LLM configuration and API settings
│   ├── llm_call.py      # LLM API interaction utilities
│   └── llm_call_test.py # Example usage script
├── utils/               # Utility functions and helpers
│   ├── db_config.py     # Database configuration
│   ├── search.py        # Search utilities
│   ├── db_schema.json   # Database schema definition
│   ├── guidance.txt     # System prompts and guidance
│   └── *_test.py        # Example usage scripts
├── workflow_test.ipynb  # Jupyter notebook demonstrating the workflow
└── requirements.txt     # Project dependencies
```

## Dependencies

- Python 3.8 or higher
- PostgreSQL database
- Access to either DeepSeek or Gemini API

Key Python packages:
- requests: HTTP requests for API calls
- python-dotenv: Environment variable management
- fuzzywuzzy: String matching and search
- python-Levenshtein: Improves fuzzywuzzy performance
- sqlalchemy: Database ORM
- pandas: Data manipulation
- numpy: Numerical computations
- psycopg2-binary: PostgreSQL adapter
- matplotlib: Data visualization
- seaborn: Statistical data visualization

For a complete list of dependencies, see `requirements.txt`.