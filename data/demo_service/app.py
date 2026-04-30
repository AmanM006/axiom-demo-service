"""
AXIOM Demo Service — Fixed version with all bugs resolved.
"""

from flask import Flask, request, jsonify
from collections import deque
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.environ.get("DATABASE_URL", "demo.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )""")
    conn.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES ('u_001', 'Alice', 'alice@example.com')")
    conn.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES ('u_002', 'Bob', 'bob@example.com')")
    for i in range(10):
        conn.execute(
            "INSERT OR IGNORE INTO transactions (id, user_id, amount, status) VALUES (?, ?, ?, ?)",
            (i + 1, f"u_00{(i % 2) + 1}", round(10.0 + i * 7.5, 2), "completed"),
        )
    conn.commit()
    conn.close()


# FIX: Use bounded deque instead of unbounded list
cache = deque(maxlen=1000)


@app.route("/process-image", methods=["POST"])
def process_image():
    data = request.get_json(force=True, silent=True) or {}
    image_data = data.get("image", "placeholder_image_data")
    # FIX: deque with maxlen auto-evicts oldest entries
    cache.append(image_data)
    return jsonify({"status": "processed", "cache_size": len(cache)})


@app.route("/handle-request", methods=["POST"])
def handle_request_endpoint():
    payload = request.get_json(force=True, silent=True) or {}
    # FIX: Use .get() with validation instead of direct key access
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400
    return jsonify({"status": "ok", "user_id": user_id})


@app.route("/user/<user_id>/transactions", methods=["GET"])
def get_user_transactions(user_id):
    conn = get_db()
    # FIX: Added WHERE clause to filter by user_id
    rows = conn.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return jsonify({"user_id": user_id, "transactions": [dict(r) for r in rows], "count": len(rows)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "demo-service"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
