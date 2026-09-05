import streamlit as st
import pandas as pd
from src.database import init_db, get_db_schema_for_llm
from src.agent.graph import create_sql_agent_graph

st.set_page_config(page_title="Self-Correcting SQL Agent", layout="wide")

st.title("🤖 Self-Correcting SQL Analytics Agent")
st.markdown("Natural Language to SQL with LangGraph Cyclical Schema & Error Reflection")

# Init DB and Agent once
@st.cache_resource
def load_resources():
    init_db()
    schema = get_db_schema_for_llm()
    agent = create_sql_agent_graph()
    return schema, agent

schema, agent = load_resources()

with st.sidebar:
    st.header("Database Schema")
    st.code(schema, language="sql")

question = st.text_input(
    "Ask a question about your healthcare database:",
    placeholder="e.g., Which doctor has the highest total earnings from completed appointments?"
)

if st.button("Run Analytics Agent", type="primary") and question:
    with st.spinner("Agent running state machine..."):
        initial_state = {
            "question": question,
            "schema": schema,
            "current_sql": "",
            "execution_error": None,
            "query_columns": [],
            "query_rows": [],
            "retry_count": 0,
            "final_response": "",
            "history": []
        }
        
        result = agent.invoke(initial_state)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Agent Execution Trail")
        for step in result["history"]:
            with st.expander(f"Step: {step['step']}", expanded=True):
                st.json(step)

    with col2:
        st.subheader("Final Executed SQL")
        st.code(result["current_sql"], language="sql")

        st.subheader("Query Results")
        if result["query_rows"]:
            df = pd.DataFrame(result["query_rows"], columns=result["query_columns"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No rows returned or query failed.")

        st.subheader("Synthesized Insight")
        st.write(result["final_response"])