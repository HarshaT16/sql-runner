"use client"; // Next.js directive indicating this is a client-side component

import { useState } from "react"; // Import useState hook to manage component state

export default function Home() {
  // -----------------------------
  // React State Variables
  // -----------------------------
  const [query, setQuery] = useState(""); // Stores the SQL query typed by the user
  const [result, setResult] = useState(null); // Stores the result returned from backend (SELECT or message)
  const [loading, setLoading] = useState(false); // Tracks whether the query is being executed
  const [error, setError] = useState(""); // Stores any error message

  // -----------------------------
  // Function to Run SQL Query
  // -----------------------------
  async function runQuery() {
    setLoading(true); // Show loading message
    setError("");     // Reset previous error
    setResult(null);  // Clear previous results

    try {
      // Send SQL query to backend API
      const res = await fetch("http://127.0.0.1:8000/api/run", {
        method: "POST", // POST request
        headers: {
          "Content-Type": "application/json", // JSON payload
        },
        body: JSON.stringify({ sql: query }), // Send query as JSON
      });

      // Parse JSON response from backend
      const data = await res.json();

      // If HTTP status is not 200 OK, show error
      if (!res.ok) {
        setError(data.detail || "Something went wrong");
      } else {
        // Store backend response (could be SELECT results or a success message)
        setResult(data);
      }
    } catch (err) {
      // If fetch fails (e.g., backend not running), show error
      setError("Failed to connect to backend");
    }

    setLoading(false); // Stop loading indicator
  }

  // -----------------------------
  // JSX Rendering
  // -----------------------------
  return (
    <div style={{ padding: "40px", maxWidth: "900px", margin: "auto" }}>
      {/* Page Title */}
      <h1 style={{ fontSize: "32px", marginBottom: "20px" }}>
        SQL Runner (Frontend)
      </h1>

      {/* Query Input Area */}
      <textarea
        placeholder="Write SQL query here..."
        value={query} // Controlled input using state
        onChange={(e) => setQuery(e.target.value)} // Update state on typing
        style={{
          width: "100%",
          height: "150px",
          padding: "10px",
          fontSize: "16px",
          fontFamily: "monospace", // Monospace for SQL readability
        }}
      />

      {/* Run Query Button */}
      <button
        onClick={runQuery} // Calls runQuery() on click
        style={{
          marginTop: "20px",
          padding: "12px 30px",
          fontSize: "18px",
          cursor: "pointer",
        }}
      >
        Run Query
      </button>

      {/* -----------------------------
          Loading Indicator
      ----------------------------- */}
      {loading && <p style={{ marginTop: "20px" }}>Running query...</p>}

      {/* -----------------------------
          Error Message
      ----------------------------- */}
      {error && (
        <p style={{ marginTop: "20px", color: "red", fontWeight: "bold" }}>
          {error}
        </p>
      )}

      {/* -----------------------------
          Display Results for SELECT Queries
      ----------------------------- */}
      {result && result.columns && result.rows && (
        <div style={{ marginTop: "20px" }}>
          <h2>Results:</h2>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                {result.columns.map((col) => (
                  <th
                    key={col} // Unique key for React rendering
                    style={{ border: "1px solid #ccc", padding: "8px", textAlign: "left" }}
                  >
                    {col} {/* Column Name */}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.rows.map((row, idx) => (
                <tr key={idx}>
                  {result.columns.map((col) => (
                    <td
                      key={col} // Unique key per cell
                      style={{ border: "1px solid #ccc", padding: "8px" }}
                    >
                      {row[col]} {/* Cell value */}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* -----------------------------
          Display Message for Non-SELECT Queries
          e.g., INSERT, UPDATE, DELETE, CREATE
      ----------------------------- */}
      {result && result.message && (
        <p style={{ marginTop: "20px", color: "green", fontWeight: "bold" }}>
          {result.message}{" "}
          {result.rows_affected !== undefined
            ? `(${result.rows_affected} rows affected)` // Show number of rows affected
            : ""}
        </p>
      )}
    </div>
  );
}
