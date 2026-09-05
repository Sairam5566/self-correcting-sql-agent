import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.config import GEMINI_API_KEY
from src.schemas import SQLGenerationOutput, SQLReflectionOutput
from src.prompts import GENERATE_SQL_PROMPT, REFLECT_AND_FIX_PROMPT, SYNTHESIZE_RESPONSE_PROMPT
from src.database import execute_sql_query
from src.agent.state import AgentState

# Ensure the Google API Key is read
api_key = GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
    api_key=api_key
)

def generate_sql_node(state: AgentState) -> dict:
    """Node 1: Generates initial SQL query using structured output."""
    prompt = PromptTemplate.from_template(GENERATE_SQL_PROMPT).format(
        schema=state["schema"],
        question=state["question"]
    )
    
    structured_llm = llm.with_structured_output(SQLGenerationOutput)
    result = structured_llm.invoke(prompt)
    
    return {
        "current_sql": result.sql_query,
        "history": state["history"] + [{"step": "initial_generation", "query": result.sql_query, "reasoning": result.reasoning}]
    }

def execute_sql_node(state: AgentState) -> dict:
    """Node 2: Executes the current SQL and updates state with rows or errors."""
    query = state["current_sql"]
    exec_result = execute_sql_query(query)
    
    return {
        "query_columns": exec_result["columns"],
        "query_rows": exec_result["rows"],
        "execution_error": exec_result["error"]
    }

def reflect_and_fix_node(state: AgentState) -> dict:
    """Node 3: Reflects on SQLite error and corrects the SQL query."""
    prompt = PromptTemplate.from_template(REFLECT_AND_FIX_PROMPT).format(
        schema=state["schema"],
        question=state["question"],
        failing_query=state["current_sql"],
        error_message=state["execution_error"]
    )
    
    structured_llm = llm.with_structured_output(SQLReflectionOutput)
    result = structured_llm.invoke(prompt)
    
    return {
        "current_sql": result.corrected_sql_query,
        "retry_count": state["retry_count"] + 1,
        "history": state["history"] + [{
            "step": f"reflection_retry_{state['retry_count'] + 1}",
            "error_caught": state["execution_error"],
            "analysis": result.error_analysis,
            "corrected_query": result.corrected_sql_query
        }]
    }

def synthesize_response_node(state: AgentState) -> dict:
    """Node 4: Formats raw data tuples into a concise analytical summary."""
    if state["execution_error"]:
        return {
            "final_response": f"Failed to execute query after {state['retry_count']} retries. Last error: {state['execution_error']}"
        }
        
    prompt = PromptTemplate.from_template(SYNTHESIZE_RESPONSE_PROMPT).format(
        question=state["question"],
        query=state["current_sql"],
        columns=state["query_columns"],
        rows=state["query_rows"]
    )
    
    response = llm.invoke(prompt)
    
    # Parse list of content blocks if returned by the SDK
    if isinstance(response.content, list):
        text_output = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in response.content
        )
    else:
        text_output = str(response.content)

    return {"final_response": text_output.strip()}