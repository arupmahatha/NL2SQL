import streamlit as st
import pandas as pd
from engine.generator import SQLGenerator
from engine.entity_extractor import EntityExtractor
from engine.value_matcher import ValueMatcher
from engine.refiner import SQLRefiner
from engine.executor import SQLExecutor
from engine.analyzer import SQLAnalyzer
from engine.visualizer import SQLVisualizer
from engine.schema_engine import SchemaEngine

st.set_page_config(page_title="NL Analytics Tool", layout="wide")
st.title("Natural Language Analytics Tool")

# Sidebar for API key and DB upload only
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("DeepSeek API Key", type="password")
    db_file = st.file_uploader(
        "Upload your data file",
        type=["db", "sqlite", "sqlite3", "csv", "xlsx", "xls"]
    )

engine = None
schema_info = None
if db_file is not None:
    try:
        with st.spinner("Processing uploaded file..."):
            engine, schema_info = SchemaEngine.from_upload(db_file)
        st.success(f"Successfully loaded {db_file.name}")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        engine = None
        schema_info = None

# Main area for query and results
st.header("Ask your question")
user_query = st.text_area("Describe what you want to analyze:", height=100)

if 'run_workflow' not in st.session_state:
    st.session_state['run_workflow'] = False

if st.button("Analyze Data"):
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

    # --- Workflow steps ---
    with st.spinner("Generating SQL query..."):
        generator = SQLGenerator()
        try:
            sql_result = generator.main_generator(user_query, api_key, schema_info)
            generated_sql = sql_result['generated_sql']
        except Exception as e:
            st.error(f"SQL Generation Error: {e}")
            st.stop()

    with st.spinner("Extracting entities..."):
        extractor = EntityExtractor()
        try:
            entities = extractor.main_entity_extractor(generated_sql, api_key)
        except Exception as e:
            st.error(f"Entity Extraction Error: {e}")
            st.stop()

    with st.spinner("Matching values..."):
        matcher = ValueMatcher()
        value_mappings = []
        try:
            for entity in entities:
                matches = matcher.main_value_matcher(entity, engine=engine)
                value_mappings.extend(matches)
        except Exception as e:
            st.error(f"Value Matching Error: {e}")
            st.stop()

    with st.spinner("Refining SQL query..."):
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

    st.header("Results")
    with st.spinner("Executing SQL query..."):
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

    st.header("Analysis")
    with st.spinner("Analyzing results..."):
        analyzer = SQLAnalyzer()
        try:
            analysis = analyzer.main_analyzer(user_query, results, api_key)['analysis']
            st.markdown(analysis, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Analysis Error: {e}")

    st.header("Visualizations")
    with st.spinner("Generating visualization..."):
        visualizer = SQLVisualizer()
        try:
            viz_code = visualizer.main_visualizer(user_query, results, api_key)['generated_code']

            import matplotlib.pyplot as plt
            import seaborn as sns
            import io
            import contextlib
            
            # Configure matplotlib for better quality in Streamlit
            plt.rcParams['figure.dpi'] = 300
            plt.rcParams['savefig.dpi'] = 300
            plt.rcParams['figure.figsize'] = (10, 6)
            plt.rcParams['font.size'] = 12
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['axes.labelsize'] = 12
            plt.rcParams['xtick.labelsize'] = 10
            plt.rcParams['ytick.labelsize'] = 10
            
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
                    # Clear any existing figures
                    plt.close('all')
                    
                    # Execute the visualization code
                    exec(viz_code, {}, local_vars)
                    
                    # Get all figures after execution
                    all_figures = plt.get_fignums()
                    
                    if all_figures:
                        for fig_num in all_figures:
                            fig = plt.figure(fig_num)
                            if fig.get_axes():  # Only display if figure has axes
                                # Set high DPI for better quality
                                fig.set_dpi(300)
                                st.pyplot(fig, use_container_width=True)
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
                                plt.figure(figsize=(12, 8), dpi=300)
                                df[categorical_cols[0]].value_counts().plot(kind='bar')
                                plt.title(f'Count of {categorical_cols[0]}')
                                plt.xticks(rotation=45, ha='right')
                                plt.tight_layout()
                                st.pyplot(plt.gcf(), use_container_width=True)
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
    st.info("Upload your data file, enter your API key, and describe what you want to analyze.") 