import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "documents.db"


def init_db(db_path=DB_PATH):
    """Create the documents table; adds the source_name column to older schemas."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL,
            source_name TEXT
        )
        """
    )

    # Migration: add the source_name column to older tables that don't have it.
    existing_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(documents)")
    }
    if "source_name" not in existing_columns:
        conn.execute("ALTER TABLE documents ADD COLUMN source_name TEXT")

    conn.commit()
    conn.close()


def insert_document(content, embedding, source_name=None, db_path=DB_PATH):
    """Save a text chunk to the database along with its embedding and source name."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO documents (content, embedding, source_name) VALUES (?, ?, ?)",
        (content, json.dumps(embedding), source_name),
    )
    conn.commit()
    conn.close()


def get_source_names(db_path=DB_PATH):
    """Return the distinct source_name values from the documents table, sorted."""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT DISTINCT source_name FROM documents "
        "WHERE source_name IS NOT NULL ORDER BY source_name"
    )
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names


def get_all_documents(db_path=DB_PATH):
    """Return all documents from the database, decoding embeddings from JSON."""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT id, content, embedding, source_name FROM documents")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row_id,
            "content": content,
            "embedding": json.loads(embedding),
            "source_name": source_name,
        }
        for row_id, content, embedding, source_name in rows
    ]
