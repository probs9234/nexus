import sqlite3
import json
import os
from typing import List

DB_FILE = "nexus_metadata.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            filename TEXT,
            encryption_key BLOB,
            size INTEGER,
            shards TEXT  -- JSON list of shard IDs
        )
    ''')
    conn.commit()
    conn.close()

def save_file_metadata(file_id: str, filename: str, encryption_key: bytes, size: int, shards: List[str]):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (file_id, filename, encryption_key, size, shards) VALUES (?, ?, ?, ?, ?)",
        (file_id, filename, encryption_key, size, json.dumps(shards))
    )
    conn.commit()
    conn.close()

def get_file_metadata(file_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, encryption_key, size, shards FROM files WHERE file_id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "filename": row[0],
            "encryption_key": row[1],
            "size": row[2],
            "shards": json.loads(row[3])
        }
    return None
