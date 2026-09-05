import sqlite3
from typing import Dict, List, Any
from src.config import DB_PATH

def init_db(db_path: str = DB_PATH) -> None:
    """Initializes tables and inserts mock healthcare analytics data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT CHECK(gender IN ('M', 'F', 'Other')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        hourly_rate REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date DATE NOT NULL,
        status TEXT CHECK(status IN ('Scheduled', 'Completed', 'Cancelled')),
        fee REAL NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        medication_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        cost REAL NOT NULL,
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM patients;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO patients (first_name, last_name, date_of_birth, gender) VALUES (?, ?, ?, ?)
        """, [
            ("Aarav", "Sharma", "1988-04-12", "M"),
            ("Priya", "Nair", "1995-09-23", "F"),
            ("Rohan", "Verma", "1972-11-05", "M"),
            ("Sneha", "Patel", "2001-02-18", "F"),
            ("Ananya", "Iyer", "1990-07-30", "F")
        ])

        cursor.executemany("""
        INSERT INTO doctors (name, specialization, hourly_rate) VALUES (?, ?, ?)
        """, [
            ("Dr. Rajesh Gupta", "Cardiology", 150.00),
            ("Dr. Meera Sen", "Dermatology", 100.00),
            ("Dr. Vikram Malhotra", "Orthopedics", 130.00),
            ("Dr. Sunita Rao", "Pediatrics", 90.00)
        ])

        cursor.executemany("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, fee) VALUES (?, ?, ?, ?, ?)
        """, [
            (1, 1, "2026-01-10", "Completed", 150.00),
            (2, 2, "2026-01-15", "Completed", 100.00),
            (3, 3, "2026-02-01", "Completed", 130.00),
            (4, 4, "2026-02-10", "Cancelled", 0.00),
            (1, 1, "2026-03-05", "Scheduled", 150.00),
            (5, 2, "2026-03-12", "Completed", 100.00),
            (3, 1, "2026-03-18", "Completed", 150.00)
        ])

        cursor.executemany("""
        INSERT INTO prescriptions (appointment_id, medication_name, dosage, cost) VALUES (?, ?, ?, ?)
        """, [
            (1, "Atorvastatin", "20mg daily", 25.50),
            (1, "Aspirin", "75mg daily", 5.00),
            (2, "Tretinoin Cream", "0.05% nightly", 45.00),
            (3, "Ibuprofen", "400mg as needed", 12.00),
            (6, "Hydrocortisone", "1% topical", 18.00),
            (7, "Metoprolol", "50mg daily", 30.00)
        ])

        conn.commit()

    conn.close()

def get_db_schema_for_llm(db_path: str = DB_PATH) -> str:
    """Introspects SQLite schema and formats it for prompt injection."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    schema_docs: List[str] = []

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        col_descriptions = [f"{col[1]} ({col[2]})" + (" PRIMARY KEY" if col[5] else "") for col in columns]

        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fk_list = cursor.fetchall()
        fk_descriptions = [f"FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})" for fk in fk_list]

        table_repr = f"Table: {table}\n  Columns: {', '.join(col_descriptions)}"
        if fk_descriptions:
            table_repr += f"\n  Foreign Keys: {', '.join(fk_descriptions)}"

        schema_docs.append(table_repr)

    conn.close()
    return "\n\n".join(schema_docs)

def execute_sql_query(query: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Executes SQL and captures raw results or exact database engine errors."""
    # Clean SQL string of markdown code blocks if the LLM accidentally added them
    clean_query = query.strip().replace("```sql", "").replace("```", "").strip()
    
    # Block unsafe mutation commands
    prohibited = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    if any(clean_query.upper().startswith(kw) for kw in prohibited):
        return {"columns": [], "rows": [], "error": "Destructive query detected. Only SELECT statements are permitted."}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(clean_query)
        columns = [description[0] for description in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        conn.close()
        return {"columns": columns, "rows": rows, "error": None}
    except sqlite3.Error as e:
        return {"columns": [], "rows": [], "error": f"SQLite Error: {str(e)}"}