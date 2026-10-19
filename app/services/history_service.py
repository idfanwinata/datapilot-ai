
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Database disimpan di folder utama proyek.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "diagnosis_history.db"


def get_connection():
    """Membuka koneksi database riwayat diagnosis."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_history_db():
    """Membuat tabel jika belum tersedia."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS diagnosis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application TEXT NOT NULL,
                error_log TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_diagnosis(application, error_log, result):
    """Menyimpan hasil analisis diagnosis RAG."""
    analysis = result.get("analysis", {})
    sources = result.get("sources", [])

    init_history_db()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO diagnosis_history (
                application,
                error_log,
                analysis_json,
                sources_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                application,
                error_log,
                json.dumps(analysis, ensure_ascii=False),
                json.dumps(sources, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        return cursor.lastrowid


def list_diagnoses(limit=20):
    """Mengambil riwayat terbaru."""
    init_history_db()

    limit = max(1, min(int(limit), 100))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, application, error_log, created_at
            FROM diagnosis_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_diagnosis(diagnosis_id):
    """Mengambil detail satu diagnosis."""
    init_history_db()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM diagnosis_history
            WHERE id = ?
            """,
            (diagnosis_id,),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    result["analysis"] = json.loads(result.pop("analysis_json"))
    result["sources"] = json.loads(result.pop("sources_json"))

    return result
