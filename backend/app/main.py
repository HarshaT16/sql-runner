# Import necessary modules
from fastapi import FastAPI, HTTPException  # FastAPI framework and HTTP exceptions
from fastapi.middleware.cors import CORSMiddleware  # To handle CORS requests
from pydantic import BaseModel  # For request body validation
import sqlite3  # SQLite database module

# Path to SQLite database file
DB_PATH = "../db/sql_runner.db"  # Relative path from backend folder

# Initialize FastAPI application
app = FastAPI(title="SQL Runner API")

# -----------------------------
# CORS Middleware Configuration
# -----------------------------
# This allows the frontend (running on localhost:3000 or any origin during development)
# to make requests to this backend without being blocked by CORS policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow requests from localhost:3000 and all origins (*)
    allow_credentials=True,  # Allow cookies or credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# -----------------------------
# Request Body Model
# -----------------------------
# This defines the expected JSON payload for /api/run
# Example: { "sql": "SELECT * FROM Customers;" }
class QueryRequest(BaseModel):
    sql: str  # SQL query as a string


# -----------------------------
# Helper Function: Database Connection
# -----------------------------
def get_db_connection():
    """
    Create a connection to the SQLite database and
    set row_factory to sqlite3.Row so that rows
    can be accessed like dictionaries (row["column_name"]).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# API Endpoint: Execute SQL Query
# -----------------------------
@app.post("/api/run")
def run_query(payload: QueryRequest):
    """
    Accepts a SQL query from the frontend, executes it,
    and returns either the query results (for SELECT queries)
    or a success message (for INSERT/UPDATE/DELETE/CREATE queries).
    """
    sql = payload.sql.strip()  # Remove leading/trailing spaces

    # If the query is empty, return a 400 error
    if not sql:
        raise HTTPException(status_code=400, detail="Empty query")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Execute the SQL query
        cur.execute(sql)

        # Determine query type by checking the first word
        first_word = sql.split()[0].lower()

        # -----------------------------
        # SELECT / PRAGMA / WITH Queries
        # -----------------------------
        # These queries return rows and columns
        if first_word in ("select", "pragma", "with"):
            rows = cur.fetchall()  # Fetch all rows
            cols = [d[0] for d in cur.description] if cur.description else []  # Get column names

            return {
                "query_type": "SELECT",  # Indicate type of query
                "columns": cols,  # Column names
                "rows": [dict(row) for row in rows]  # Convert rows to dictionaries
            }

        # -----------------------------
        # Non-SELECT Queries
        # -----------------------------
        # INSERT, UPDATE, DELETE, CREATE, etc.
        else:
            conn.commit()  # Save changes to the database
            return {
                "query_type": first_word.upper(),  # e.g., INSERT, UPDATE
                "message": f"{first_word.upper()} query executed successfully",
                "rows_affected": cur.rowcount  # Number of rows affected by the query
            }

    except sqlite3.Error as e:
        # Catch database errors and return as HTTP 400
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        # Ensure database connection is always closed
        conn.close()


# -----------------------------
# API Endpoint: List All Tables
# -----------------------------
@app.get("/api/tables")
def list_tables():
    """
    Returns a list of all user-created tables in the SQLite database.
    System tables (starting with 'sqlite_') are excluded.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = [row[0] for row in cur.fetchall()]  # Extract table names from result
        return {"tables": tables}
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


# -----------------------------
# API Endpoint: Get Table Info
# -----------------------------
@app.get("/api/table/{table_name}")
def table_info(table_name: str):
    """
    Returns detailed information about a specific table:
    - Column metadata: name, type, default value, primary key, etc.
    - Sample data: first 5 rows from the table
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Fetch column information using PRAGMA
        cur.execute(f"PRAGMA table_info({table_name});")
        cols = [
            {"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "default": r[4], "pk": r[5]}
            for r in cur.fetchall()
        ]

        # Fetch first 5 rows of the table as sample
        cur.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        sample = [dict(row) for row in cur.fetchall()]

        return {"columns": cols, "sample": sample}

    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        conn.close()
