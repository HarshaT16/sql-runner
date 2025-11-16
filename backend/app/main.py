# Import necessary modules
from fastapi import FastAPI, HTTPException  # FastAPI framework and HTTP exceptions
from fastapi.middleware.cors import CORSMiddleware  # To handle CORS requests
from fastapi.responses import HTMLResponse  # To return HTML from root route
from pydantic import BaseModel  # For request body validation
import sqlite3  # SQLite database module

# Path to SQLite database file
DB_PATH = "../db/sql_runner.db"  # Relative path from backend folder

# Initialize FastAPI application
app = FastAPI(title="SQL Runner API")

# -----------------------------
# CORS Middleware Configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow requests from frontend and all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# -----------------------------
# Request Body Model
# -----------------------------
class QueryRequest(BaseModel):
    sql: str  # SQL query as a string

# -----------------------------
# Helper Function: Database Connection
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# -----------------------------
# Root Route (HTML Welcome Page)
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def root():
    """
    Root route showing a simple HTML welcome page.
    Provides information and a link to the frontend.
    """
    return """
    <html>
        <head>
            <title>SQL Runner API</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>Welcome to SQL Runner API</h1>
            <p>This is the backend API for your SQL Runner project.</p>
            <p>Frontend UI: <a href="http://localhost:3000" target="_blank">Click here to open SQL Runner Frontend</a></p>
            <p>API Endpoints:</p>
            <ul>
                <li>POST /api/run - Execute SQL queries</li>
                <li>GET /api/tables - List all tables</li>
                <li>GET /api/table/{table_name} - Table schema & sample data</li>
            </ul>
        </body>
    </html>
    """

# -----------------------------
# API Endpoint: Execute SQL Query
# -----------------------------
@app.post("/api/run")
def run_query(payload: QueryRequest):
    sql = payload.sql.strip()
    if not sql:
        raise HTTPException(status_code=400, detail="Empty query")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)
        first_word = sql.split()[0].lower()

        # SELECT / PRAGMA / WITH Queries
        if first_word in ("select", "pragma", "with"):
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            return {
                "query_type": "SELECT",
                "columns": cols,
                "rows": [dict(row) for row in rows]
            }
        # Non-SELECT Queries (INSERT, UPDATE, DELETE, CREATE, etc.)
        else:
            conn.commit()
            return {
                "query_type": first_word.upper(),
                "message": f"{first_word.upper()} query executed successfully",
                "rows_affected": cur.rowcount
            }

    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# -----------------------------
# API Endpoint: List All Tables
# -----------------------------
@app.get("/api/tables")
def list_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = [row[0] for row in cur.fetchall()]
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
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get column info
        cur.execute(f"PRAGMA table_info({table_name});")
        cols = [
            {"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "default": r[4], "pk": r[5]}
            for r in cur.fetchall()
        ]
        # Get first 5 rows
        cur.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        sample = [dict(row) for row in cur.fetchall()]
        return {"columns": cols, "sample": sample}
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

