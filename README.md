# NL2SQL Workflow System

A sophisticated Natural Language to SQL conversion system that leverages Large Language Models (LLMs) to generate, refine, and analyze SQL queries from natural language input. The system provides a complete workflow from natural language query to SQL execution and visualization.

## System Architecture

The system is built with a modular architecture consisting of several key components:

### 1. LLM Configuration (`llm_config/`)
- Manages interactions with DeepSeek LLM API
- Handles API calls, conversation history, and response formatting
- Maintains conversation context for improved response quality

### 2. Core Engine Components (`engine/`)

#### SQL Generator
- Converts natural language queries into SQL using LLMs
- Integrates schema information for context-aware generation
- Supports complex queries with JOINs, subqueries, and aggregations
- Ensures SQL syntax correctness and completeness

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
- Analyzes query execution results using LLM
- Provides insights and explanations
- Generates human-readable summaries

#### SQL Visualizer
- Generates Python visualization code for query results
- Uses LLM to create appropriate visualizations based on data
- Supports various chart types and data representations
- Ensures clean and reusable visualization code

#### Schema Engine
- Handles database schema extraction and management
- Supports multiple database formats (SQLite, CSV, Excel)
- Provides schema information for SQL generation

### 3. Utilities (`utils/`)
- Database Utilities: Manages database connections and operations
- Search Utilities: Provides fuzzy search and matching capabilities
- Schema Files: Contains database schema definitions in JSON format

## Setup and Configuration

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Running the Application**
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Start the Application**
   - Run `streamlit run app.py`
   - The application will open in your web browser

2. **Configure the Setup**
   - Enter your DeepSeek API key in the sidebar
   - Upload a database file (SQLite, CSV, Excel)

3. **Query Processing**
   - Enter your natural language query in the text area
   - Click "Run Full Workflow" to process the query
   - View the generated SQL, extracted entities, and execution results
   - Explore visualizations and LLM analysis of the results

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── engine/                # Core SQL generation and processing engine
│   ├── generator.py       # SQL query generation
│   ├── entity_extractor.py # Entity extraction from SQL
│   ├── value_matcher.py   # Value matching utilities
│   ├── refiner.py        # SQL query refinement
│   ├── executor.py       # SQL query execution
│   ├── analyzer.py       # Result analysis
│   ├── visualizer.py     # Query result visualization
│   └── schema_engine.py  # Database schema handling
├── llm_config/           # LLM configuration and API settings
│   └── llm_call.py      # LLM API interaction utilities
├── utils/               # Utility functions and helpers
│   └── search.py        # Search utilities
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Features

- **Natural Language to SQL**: Convert plain English queries to SQL
- **Multi-format Database Support**: Works with SQLite, CSV, and Excel files
- **Entity Extraction**: Automatically identifies and validates database entities
- **Value Matching**: Ensures data consistency and accuracy
- **SQL Refinement**: Optimizes and improves generated SQL queries
- **Result Analysis**: LLM-powered analysis of query results
- **Data Visualization**: Automatic generation of appropriate charts and graphs
- **Interactive Web Interface**: User-friendly Streamlit application
- **Secure API Key Handling**: API keys are only taken from user input, not environment variables

## Dependencies

- Python 3.8 or higher
- Access to DeepSeek API

Key Python packages:
- streamlit: Web application framework
- requests: HTTP requests for API calls
- fuzzywuzzy: String matching and search
- python-Levenshtein: Improves fuzzywuzzy performance
- sqlalchemy: Database ORM
- pandas: Data manipulation
- numpy: Numerical computations
- matplotlib: Data visualization
- seaborn: Statistical data visualization

For a complete list of dependencies, see `requirements.txt`.