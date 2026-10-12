# =====================================================================
# 💾 PERSISTENT SQLITE DATABASE (USERS, THREADS & CHAT HISTORY)
# =====================================================================

import os
import sqlite3
import uuid
import bcrypt

# Ensure the SQLite DB resolves absolute to this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "triage_app.db")


def init_db():
    """Initializes tables for accounts, project threads, and chat history."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash BLOB NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    # Migration check: add is_pinned column if database was created with older schema
    cur.execute("PRAGMA table_info(threads)")
    columns = [col[1] for col in cur.fetchall()]
    if "is_pinned" not in columns:
        cur.execute("ALTER TABLE threads ADD COLUMN is_pinned INTEGER DEFAULT 0")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (thread_id) REFERENCES threads(thread_id)
        )
    """)
    conn.commit()
    conn.close()


def register_user(username: str, password: str) -> bool:
    """Hashes password with bcrypt and registers a new account."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return False
    pwd_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
    conn.commit()
    conn.close()
    return True


def verify_user(username: str, password: str) -> bool:
    """Verifies cleartext password against the stored bcrypt hash."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), row[0])


def get_user_threads(username: str) -> list[dict]:
    """Retrieves all project threads owned by a user, sorted by pinned status then creation date."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(threads)")
    columns = [col[1] for col in cur.fetchall()]

    if "is_pinned" in columns:
        cur.execute(
            """
            SELECT thread_id, title, is_pinned 
            FROM threads 
            WHERE username = ? 
            ORDER BY is_pinned DESC, created_at DESC
            """,
            (username,)
        )
        rows = cur.fetchall()
        conn.close()
        return [{"thread_id": r[0], "title": r[1], "is_pinned": bool(r[2])} for r in rows]
    else:
        cur.execute(
            "SELECT thread_id, title FROM threads WHERE username = ? ORDER BY created_at DESC",
            (username,)
        )
        rows = cur.fetchall()
        conn.close()
        return [{"thread_id": r[0], "title": r[1], "is_pinned": False} for r in rows]


def create_thread(username: str, title: str) -> str:
    """Creates a new project thread for an isolated triage scope."""
    thread_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO threads (thread_id, username, title, is_pinned) VALUES (?, ?, ?, 0)",
        (thread_id, username, title)
    )
    conn.commit()
    conn.close()
    return thread_id


def rename_thread(thread_id: str, new_title: str):
    """Updates the display title of a thread."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE threads SET title = ? WHERE thread_id = ?", (new_title, thread_id))
    conn.commit()
    conn.close()


def toggle_pin_thread(thread_id: str):
    """Toggles the pinned status (0 or 1) of a thread."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE threads SET is_pinned = CASE WHEN is_pinned = 1 THEN 0 ELSE 1 END WHERE thread_id = ?",
        (thread_id,)
    )
    conn.commit()
    conn.close()


def delete_thread(thread_id: str):
    """Deletes a thread and cascades message deletion for that thread."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
    cur.execute("DELETE FROM threads WHERE thread_id = ?", (thread_id,))
    conn.commit()
    conn.close()


def get_thread_messages(thread_id: str) -> list[dict]:
    """Retrieves historical messages for a given thread in chronological order."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM messages WHERE thread_id = ? ORDER BY id ASC",
        (thread_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]


def add_message(thread_id: str, role: str, content: str):
    """Appends a new conversational message to the persistent store."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
        (thread_id, role, content)
    )
    conn.commit()
    conn.close()