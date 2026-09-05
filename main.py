import json
from tabulate import tabulate
from src.database import init_db, get_db_schema_for_llm
from src.agent.graph import create_sql_agent_graph

def run_cli():
    print("=" * 60)
    print(" Self-Correcting SQL Analytics Agent (CLI) ")
    print("=" * 60)
    
    # Initialize DB and Schema
    init_db()
    schema = get_db_schema_for_llm()
    agent = create_sql_agent_graph()

    while True:
        try:
            question = input("\nEnter your question (or 'exit' to quit): ").strip()
            if question.lower() in ("exit", "quit", "q"):
                break
            if not question:
                continue

            print("\nAnalyzing question and planning SQL...")
            
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

            final_state = agent.invoke(initial_state)

            print("\n--- AGENT EXECUTION TRAIL ---")
            for entry in final_state["history"]:
                print(f"[{entry['step'].upper()}]")
                print(json.dumps(entry, indent=2))
                print("-" * 40)

            print("\n--- FINAL SQL ---")
            print(final_state["current_sql"])

            print("\n--- DATABASE RESULTS ---")
            if final_state["query_rows"]:
                print(tabulate(final_state["query_rows"], headers=final_state["query_columns"], tablefmt="grid"))
            else:
                print("No rows returned or query failed.")

            print("\n--- ANALYTICAL INSIGHT ---")
            print(final_state["final_response"])

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    run_cli()