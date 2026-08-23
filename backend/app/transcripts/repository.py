from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path

from app.core.errors import RuneError
from app.storage.database import connect_database
from app.transcripts.types import Transcript


class TranscriptRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect_database(database_path)
        self._lock = threading.RLock()
        self._create_schema()

    def _create_schema(self) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transcripts (
                    job_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def save(self, transcript: Transcript) -> Transcript:
        payload = json.dumps(transcript.to_dict(), ensure_ascii=False)
        now = datetime.now(UTC).isoformat()
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO transcripts (job_id, payload, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (transcript.job_id, payload, now),
            )
        return transcript

    def get(self, job_id: str) -> Transcript | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT payload FROM transcripts WHERE job_id = ?", (job_id,)
            ).fetchone()
        if row is None:
            return None
        return Transcript.from_dict(json.loads(str(row["payload"])))

    def update_text(self, job_id: str, text: str) -> Transcript:
        transcript = self.get(job_id)
        if transcript is None:
            raise RuneError(code="transcript_not_found", message="Transcript not found.")
        return self.save(transcript.with_text(text.strip()))
