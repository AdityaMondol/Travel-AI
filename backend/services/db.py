import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

DB_PATH = "manus.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        objective TEXT,
        status TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        plan JSON
    )''')

    # Tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        job_id TEXT,
        agent TEXT,
        status TEXT,
        description TEXT,
        result TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )''')

    # Artifacts table
    c.execute('''CREATE TABLE IF NOT EXISTS artifacts (
        id TEXT PRIMARY KEY,
        job_id TEXT,
        type TEXT,
        path TEXT,
        metadata JSON,
        created_at TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )''')

    # Audit Logs table
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT,
        action TEXT,
        details JSON,
        timestamp TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )''')

    conn.commit()
    conn.close()

class DBService:
    def __init__(self):
        init_db()

    def create_job(self, job_id: str, objective: str):
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO jobs (id, objective, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (job_id, objective, "queued", datetime.now(), datetime.now())
        )
        conn.commit()
        conn.close()

    def update_job_status(self, job_id: str, status: str):
        conn = get_db_connection()
        conn.execute(
            "UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now(), job_id)
        )
        conn.commit()
        conn.close()

    def log_audit(self, job_id: str, action: str, details: Dict[str, Any]):
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO audit_logs (job_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
            (job_id, action, json.dumps(details), datetime.now())
        )
        conn.commit()
        conn.close()

db_service = DBService()
