from src.database import init_db, get_db_schema_for_llm
from src.agent.graph import create_sql_agent_graph

def test_sql_agent_basic_query():
    init_db()
    schema = get_db_schema_for_llm()
    agent = create_sql_agent_graph()

    state = {
        "question": "How many total patients are registered in the database?",
        "schema": schema,
        "current_sql": "",
        "execution_error": None,
        "query_columns": [],
        "query_rows": [],
        "retry_count": 0,
        "final_response": "",
        "history": []
    }

    result = agent.invoke(state)
    assert result["execution_error"] is None
    assert len(result["query_rows"]) > 0
    assert result["query_rows"][0][0] == 5
    print("\n✅ Basic Query Test Passed!")

if __name__ == "__main__":
    test_sql_agent_basic_query()