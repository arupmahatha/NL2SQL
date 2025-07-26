import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from engine.generator import SQLGenerator
from engine.entity_extractor import EntityExtractor
from engine.value_matcher import ValueMatcher
from engine.refiner import SQLRefiner
from engine.executor import SQLExecutor
from engine.analyzer import SQLAnalyzer
from engine.visualizer import SQLVisualizer

st.set_page_config(page_title="NL2SQL Workflow", layout="wide")
st.title("Natural Language to SQL Workflow")

# 0. User API Key Input
st.header("0. Enter your DeepSeek API Key")
api_key = st.text_input("DeepSeek API Key", type="password")

# 0.1 User Database Connection Input
st.header("0.1. Connect or Upload Your Database")
db_conn_str = st.text_input("Database Connection String (SQLAlchemy format)", value="")
db_file = st.file_uploader("Or upload a SQLite/Postgres DB file", type=["db", "sqlite", "sqlite3"])

engine = None
if db_file is not None:
    # Save uploaded file to a temporary location
    import tempfile
    import os
    suffix = db_file.name.split('.')[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{suffix}') as tmp_file:
        tmp_file.write(db_file.read())
        tmp_path = tmp_file.name
    engine = create_engine(f"sqlite:///{tmp_path}")
elif db_conn_str:
    engine = create_engine(db_conn_str)

# 1. User Query Input
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
        st.error("Please provide a database connection string or upload a database file.")
        st.stop()

    # 2. SQL Generation
    st.header("2. Generated SQL")
    generator = SQLGenerator()
    try:
        sql_result = generator.main_generator(user_query)
        generated_sql = sql_result['generated_sql']
        st.code(generated_sql, language='sql')
    except Exception as e:
        st.error(f"SQL Generation Error: {e}")
        st.stop()

    # 3. Entity Extraction
    st.header("3. Extracted Entities")
    extractor = EntityExtractor()
    try:
        entities = extractor.main_entity_extractor(generated_sql)
        if entities:
            st.dataframe(pd.DataFrame(entities))
        else:
            st.info("No entities extracted.")
    except Exception as e:
        st.error(f"Entity Extraction Error: {e}")
        st.stop()

    # 4. Value Matching
    st.header("4. Value Matching Results")
    matcher = ValueMatcher()
    value_mappings = []
    try:
        for entity in entities:
            matches = matcher.main_value_matcher(entity, engine=engine)
            value_mappings.extend(matches)
        if value_mappings:
            st.dataframe(pd.DataFrame(value_mappings))
        else:
            st.info("No value mappings found.")
    except Exception as e:
        st.error(f"Value Matching Error: {e}")
        st.stop()

    # 5. SQL Refinement
    st.header("5. Refined SQL")
    refiner = SQLRefiner()
    try:
        refined_sql = refiner.main_refiner(generated_sql, value_mappings)['refined_sql']
        st.code(refined_sql, language='sql')
    except Exception as e:
        st.error(f"SQL Refinement Error: {e}")
        st.stop()

    # 6. SQL Execution
    st.header("6. SQL Execution Results")
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

    # 7. Results Analysis
    st.header("7. Results Analysis (LLM)")
    analyzer = SQLAnalyzer()
    try:
        from llm_config.llm_call import generate_text
        analysis = analyzer.main_analyzer(user_query, results, llm_func=lambda prompt: generate_text(prompt, api_key))['analysis']
        st.text_area("Analysis:", analysis, height=200)
    except Exception as e:
        st.error(f"Analysis Error: {e}")

    # 8. Results Visualization
    st.header("8. Results Visualization")
    visualizer = SQLVisualizer()
    try:
        from llm_config.llm_call import generate_text
        viz_code = visualizer.main_visualizer(user_query, results, llm_func=lambda prompt: generate_text(prompt, api_key))['generated_code']
        st.subheader("Visualization Code")
        st.code(viz_code, language='python')
        import matplotlib.pyplot as plt
        import seaborn as sns
        import io
        import contextlib
        local_vars = {'execution_results': results, 'pd': pd, 'plt': plt, 'sns': sns}
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                exec(viz_code, {}, local_vars)
                st.pyplot(plt)
            except Exception as viz_e:
                st.warning(f"Could not render visualization: {viz_e}")
    except Exception as e:
        st.error(f"Visualization Error: {e}")
else:
    st.info("Enter a query, API key, and database connection to begin.") 