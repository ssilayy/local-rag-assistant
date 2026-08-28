import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "documents.db"


def init_db(db_path=DB_PATH):
    """documents tablosunu oluşturur; eski şemaları source_name sütunuyla günceller."""
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

    # Migration: source_name sütunu olmayan eski tablolara bu sütunu ekle.
    existing_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(documents)")
    }
    if "source_name" not in existing_columns:
        conn.execute("ALTER TABLE documents ADD COLUMN source_name TEXT")

    conn.commit()
    conn.close()


def insert_document(content, embedding, source_name=None, db_path=DB_PATH):
    """Bir metin parçasını embedding'i ve kaynak adıyla birlikte veritabanına ekler."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO documents (content, embedding, source_name) VALUES (?, ?, ?)",
        (content, json.dumps(embedding), source_name),
    )
    conn.commit()
    conn.close()


def get_all_documents(db_path=DB_PATH):
    """Veritabanındaki tüm dökümanları, embedding'leri JSON'dan çözerek döndürür."""
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
