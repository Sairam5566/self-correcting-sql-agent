GENERATE_SQL_PROMPT = """You are an expert SQL analytics agent working with an SQLite database.
Given a user query and the schema definition, generate an accurate, read-only SQLite SELECT query.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

CRITICAL RULES:
1. Return ONLY a valid SQLite SELECT query.
2. Never mutate or alter data (NO DROP, DELETE, INSERT, UPDATE).
3. Ensure table and column names match the schema EXACTLY.
"""

REFLECT_AND_FIX_PROMPT = """You are a Self-Correcting SQL Debugger.
The previous SQL query failed during execution against the SQLite engine.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

FAILING SQL QUERY:
{failing_query}

DATABASE ERROR MESSAGE:
{error_message}

Analyze the error against the schema, identify the missing join, wrong column, or syntax flaw, and output the corrected SQL query.
"""

SYNTHESIZE_RESPONSE_PROMPT = """You are a helpful Data Analyst. 
Given the user's question, the SQL query executed, and the raw database result rows, provide a clean, insightful natural language summary of the findings.

USER QUESTION: {question}
SQL EXECUTED: {query}
COLUMNS: {columns}
RESULTS: {rows}
"""