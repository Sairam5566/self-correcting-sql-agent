from langgraph.graph import StateGraph, START, END
from src.config import MAX_RETRIES
from src.agent.state import AgentState
from src.agent.nodes import (
    generate_sql_node,
    execute_sql_node,
    reflect_and_fix_node,
    synthesize_response_node
)
def execution_router(state: AgentState) -> str:
    """Routes to reflection on execution errors OR empty result sets on first attempt."""
    if state["retry_count"] >= MAX_RETRIES:
        return "synthesize_response"
        
    # Standard SQLite error
    if state["execution_error"] is not None:
        return "reflect_and_fix"
        
    # Optional semantic check: If query succeeded but returned 0 rows on pass 1
    # if len(state["query_rows"]) == 0 and state["retry_count"] == 0:
    #     return "reflect_and_fix"

    return "synthesize_response"
def create_sql_agent_graph():
    """Builds and compiles the self-correcting StateGraph."""
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("reflect_and_fix", reflect_and_fix_node)
    workflow.add_node("synthesize_response", synthesize_response_node)

    # 2. Add Deterministic Edges
    workflow.add_edge(START, "generate_sql")
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_edge("reflect_and_fix", "execute_sql")
    workflow.add_edge("synthesize_response", END)

    # 3. Add Conditional Edge (Cyclical Feedback Loop)
    workflow.add_conditional_edges(
        "execute_sql",
        execution_router,
        {
            "synthesize_response": "synthesize_response",
            "reflect_and_fix": "reflect_and_fix"
        }
    )

    return workflow.compile()