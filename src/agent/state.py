from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    question: str
    schema: str
    current_sql: str
    execution_error: Optional[str]
    query_columns: List[str]
    query_rows: List[Any]
    retry_count: int
    final_response: str
    history: List[Dict[str, Any]]