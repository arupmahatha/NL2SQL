import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect
from engine.generator import SQLGenerator
from engine.entity_extractor import EntityExtractor
from engine.value_matcher import ValueMatcher
from engine.refiner import SQLRefiner
from engine.executor import SQLExecutor
from engine.analyzer import SQLAnalyzer
from engine.visualizer import SQLVisualizer
import json

st.set_page_config(page_title="NL2SQL Workflow", layout="wide")
st.title("Natural Language to SQL Workflow")

# Sidebar for API key and DB upload only
with st.sidebar:
    st.header("API & Database Setup")
    api_key = st.text_input("DeepSeek API Key", type="password")
    db_file = st.file_uploader(
        "Upload a database or data file",
        type=["db", "sqlite", "sqlite3", "csv", "xlsx", "xls"]
    )

engine = None
uploaded_df = None
schema_info = None
if db_file is not None:
    import tempfile
    import os
    suffix = db_file.name.split('.')[-1].lower()
    if suffix in ["db", "sqlite", "sqlite3"]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{suffix}') as tmp_file:
            tmp_file.write(db_file.read())
            tmp_path = tmp_file.name
        engine = create_engine(f"sqlite:///{tmp_path}")
        # Extract schema using SQLAlchemy inspector
        inspector = inspect(engine)
        formatted_schema = []
        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                col_info = f"{col['name']} ({col['type']})"
                columns.append(col_info)
            formatted_schema.append(f"Table: {table_name}\nColumns:\n" + "\n".join(f"  - {col}" for col in columns))
        schema_info = "\n\n".join(formatted_schema)
    elif suffix in ["csv"]:
        uploaded_df = pd.read_csv(db_file)
        engine = create_engine("sqlite:///:memory:")
        uploaded_df.to_sql("uploaded_table", engine, index=False, if_exists="replace")
        # Extract schema from DataFrame
        columns = [f"{col} ({str(dtype)})" for col, dtype in uploaded_df.dtypes.items()]
        schema_info = f"Table: uploaded_table\nColumns:\n" + "\n".join(f"  - {col}" for col in columns)
    elif suffix in ["xlsx", "xls"]:
        uploaded_df = pd.read_excel(db_file)
        engine = create_engine("sqlite:///:memory:")
        uploaded_df.to_sql("uploaded_table", engine, index=False, if_exists="replace")
        # Extract schema from DataFrame
        columns = [f"{col} ({str(dtype)})" for col, dtype in uploaded_df.dtypes.items()]
        schema_info = f"Table: uploaded_table\nColumns:\n" + "\n".join(f"  - {col}" for col in columns)
    else:
        st.warning("Unsupported file type. Please upload SQLite, CSV, or Excel.")
        engine = None
        schema_info = None

# Main area for query and results
st.header("1. Enter your query")
user_query = st.text_area("Type your natural language query:", height=100)

if 'run_workflow' not in st.session_state:
    st.session_state['run_workflow'] = False

if st.button("Run Full Workflow"):
    st.session_state['run_workflow'] = True

if st.session_state['run_workflow'] and user_query.strip():
    if not api_key:
        st.error("Please enter your DeepSeek API key.")
        st.stop()
    if engine is None:
        st.error("Please upload a supported database or data file.")
        st.stop()
    if schema_info is None:
        st.error("Could not extract schema from the uploaded file.")
        st.stop()

    # --- Workflow steps (hidden) ---
    generator = SQLGenerator()
    try:
        sql_result = generator.main_generator(user_query, api_key, schema_info)
        generated_sql = sql_result['generated_sql']
    except Exception as e:
        st.error(f"SQL Generation Error: {e}")
        st.stop()

    extractor = EntityExtractor()
    try:
        entities = extractor.main_entity_extractor(generated_sql, api_key)
    except Exception as e:
        st.error(f"Entity Extraction Error: {e}")
        st.stop()

    matcher = ValueMatcher()
    value_mappings = []
    try:
        for entity in entities:
            matches = matcher.main_value_matcher(entity, engine=engine)
            value_mappings.extend(matches)
    except Exception as e:
        st.error(f"Value Matching Error: {e}")
        st.stop()

    refiner = SQLRefiner()
    try:
        # If no entities were found, use the original SQL
        if not entities:
            refined_sql = generated_sql
        else:
            refined_sql = refiner.main_refiner(generated_sql, value_mappings)['refined_sql']
    except Exception as e:
        st.error(f"SQL Refinement Error: {e}")
        st.stop()

    # --- Show only executor, LLM analysis, and visualization ---
    with st.expander("Show Database Schema", expanded=False):
        if schema_info:
            st.text(schema_info)
        else:
            st.info("No schema information available.")

    with st.expander("Show Generated SQL", expanded=False):
        st.code(generated_sql, language='sql')

    with st.expander("Show Extracted Entities", expanded=False):
        if entities:
            st.dataframe(pd.DataFrame(entities))
        else:
            st.info("No entities extracted.")

    with st.expander("Show Value Matching Results", expanded=False):
        if value_mappings:
            st.dataframe(pd.DataFrame(value_mappings))
        else:
            st.info("No value mappings found.")

    with st.expander("Show Refined SQL", expanded=False):
        st.code(refined_sql, language='sql')

    st.header("SQL Execution Results")
    executor = SQLExecutor()
    try:
        success, results, formatted_results, error = executor.main_executor(refined_sql, engine)
        if not success:
            st.error(f"SQL Execution Error: {error}")
            st.stop()
        if results:
            st.dataframe(pd.DataFrame(results))
        else:
            st.info("No results returned from SQL execution.")
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        st.stop()

    st.header("Results Analysis (LLM)")
    analyzer = SQLAnalyzer()
    try:
        analysis = analyzer.main_analyzer(user_query, results, api_key)['analysis']
        with st.expander("Show LLM Analysis", expanded=False):
            st.markdown(analysis, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Analysis Error: {e}")

    st.header("Results Visualization")
    visualizer = SQLVisualizer()
    try:
        viz_code = visualizer.main_visualizer(user_query, results, api_key)['generated_code']
        with st.expander("Show Visualization Code", expanded=False):
            st.code(viz_code, language='python')

        import matplotlib.pyplot as plt
        import seaborn as sns
        import io
        import contextlib
        # Patch plt.show to a no-op so figures remain open for Streamlit
        plt.show = lambda *args, **kwargs: None
        local_vars = {
            'execution_results': results, 
            'pd': pd, 
            'plt': plt, 
            'sns': sns,
            'matplotlib': __import__('matplotlib'),
            'seaborn': __import__('seaborn')
        }
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                # Do NOT close all figures before exec!
                exec(viz_code, {}, local_vars)
                figure_numbers = plt.get_fignums()
                if figure_numbers:
                    for fig_num in figure_numbers:
                        fig = plt.figure(fig_num)
                        st.pyplot(fig)
                        plt.close(fig)
                else:
                    st.warning("No plots were generated by the visualization code.")
                    if results and isinstance(results, list) and len(results) > 0:
                        df = pd.DataFrame(results)
                        numeric_cols = df.select_dtypes(include='number').columns
                        categorical_cols = df.select_dtypes(include='object').columns
                        if len(numeric_cols) > 1:
                            st.bar_chart(df[numeric_cols])
                        elif len(numeric_cols) == 1:
                            st.bar_chart(df[numeric_cols[0]])
                        elif len(categorical_cols) > 0:
                            import matplotlib.pyplot as plt
                            import seaborn as sns
                            plt.figure(figsize=(8, 4))
                            df[categorical_cols[0]].value_counts().plot(kind='bar')
                            plt.title(f'Count of {categorical_cols[0]}')
                            st.pyplot(plt.gcf())
                            plt.close()
                        else:
                            st.dataframe(df.head())
                    else:
                        st.info("No data available to visualize.")
            except Exception as viz_e:
                st.warning(f"Could not render visualization: {viz_e}")
                st.error(f"Visualization execution error: {str(viz_e)}")
    except Exception as e:
        st.error(f"Visualization Error: {e}")
else:
    st.info("Enter a query, API key, and database file to begin.") 