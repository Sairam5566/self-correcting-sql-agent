from pydantic import BaseModel, Field

class SQLGenerationOutput(BaseModel):
    """Pydantic schema for strict SQL query generation."""
    sql_query: str = Field(description="The executable, read-only SQLite query addressing the user prompt.")
    reasoning: str = Field(description="Brief explanation of the chosen joins, filters, and projections.")

class SQLReflectionOutput(BaseModel):
    """Pydantic schema for reflection and error-correction."""
    error_analysis: str = Field(description="Identification of why the previous SQL failed based on the error.")
    corrected_sql_query: str = Field(description="The revised SQLite query fixing the syntax/schema issue.")