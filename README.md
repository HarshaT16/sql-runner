# sql-runner
# sql-runner

# SQL Runner Web Application

## Description
SQL Runner is a simple web application that allows users to execute SQL queries on a SQLite database and view the results.  
It includes a frontend built with **Next.js** and a backend using **FastAPI (Python)**.  

**Features:**
- Write and run SQL queries.
- View results in a table format.
- See available tables and table schemas.
- Supports INSERT, UPDATE, DELETE, CREATE queries with feedback.

---

## Project Structure

sql-runner/
├─ backend/ # FastAPI backend code
│ ├─ app/
│ │ └─ main.py
│ └─ requirements.txt
├─ frontend/ # Next.js frontend code
│ └─ app/
├─ db/
│ └─ sql_runner.db # SQLite database
├─ README.md
└─ .gitignore


---

# Setup Instructions (Without Docker)

# Backend Setup
1. Navigate to the backend folder:

```bash
cd backend

Install Python dependencies:

pip install -r requirements.txt


Ensure the SQLite database exists in db/sql_runner.db.
If not, create it and add sample tables (Customers, Orders, Shippings) as per project instructions.

Run the backend server:

uvicorn app.main:app --reload


The backend will be available at http://127.0.0.1:8000.

# 2 Frontend Setup

Navigate to the frontend folder:

cd frontend


Install Node.js dependencies:

npm install


Run the frontend development server:

npm run dev


Open a browser at http://localhost:3000 to use the SQL Runner.

API Endpoints (Backend)

Run Query

POST /api/run
Body: { "sql": "SELECT * FROM Customers;" }


Response:

For SELECT: { "query_type": "SELECT", "columns": [...], "rows": [...] }

For INSERT/UPDATE/DELETE/CREATE: { "query_type": "INSERT", "message": "INSERT query executed successfully", "rows_affected": 1 }

List Tables

GET /api/tables


Response: { "tables": ["Customers", "Orders", "Shippings"] }

Table Info

GET /api/table/{table_name}


Response:

{
  "columns": [{ "cid": 0, "name": "customer_id", "type": "INTEGER", ... }],
  "sample": [{ "customer_id": 1, "first_name": "John", ... }]
}
