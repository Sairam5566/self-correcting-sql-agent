# Self-Correcting SQL Analytics Agent 🤖📊

An autonomous Text-to-SQL data analytics agent powered by **LangGraph**, **Google Gemini**, and **Pydantic**. 

The system inspects relational database schemas, translates natural language prompts into executable SQLite queries, safely executes transactions, and implements a deterministic cyclical reflection loop to intercept database exceptions and self-correct syntax or schema mismatches before synthesizing the final business insight.

---

## 🏗️ Architecture & Cyclical Feedback Loop

Traditional Text-to-SQL pipelines fail when an LLM hallucinates column names or invents table joins. This agent addresses hallucinations via a state-machine execution graph:

```text
       [START]
          │
          ▼
   ┌──────────────┐
   │ generate_sql │ <──────────────────────────────┐
   └──────┬───────┘                                │
          │                                        │
          ▼                                        │ (Retry on DB Error)
   ┌──────────────┐                                │
   │ execute_sql  │ ──── (Error & retries < MAX) ──┤
   └──────┬───────┘                                │
          │                                        │
          ├────────────────────────────────────────┘
          │ (Success OR retries >= MAX)
          ▼
┌────────────────────┐
│ synthesize_response│
└─────────┬──────────┘
          │
          ▼
        [END]