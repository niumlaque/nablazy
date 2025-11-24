from __future__ import annotations

import threading
from typing import Dict, Optional


class JobStatusStore:
    """In-memory job status store."""

    def __init__(self) -> None:
        self._statuses: Dict[str, Dict[str, Optional[str]]] = {}
        self._lock = threading.Lock()

    def set_status(
        self, job_id: str, status: str, message: Optional[str] = None
    ) -> None:
        """Update or create job status."""
        with self._lock:
            self._statuses[job_id] = {"status": status, "message": message}

    def get_status(self, job_id: str) -> Dict[str, Optional[str]]:
        """Return a copy of the current status."""
        with self._lock:
            status = self._statuses.get(job_id)
            if status is None:
                return {"status": "not_found", "message": "指定されたjob_idは存在しません"}
            return dict(status)

    def clear(self, job_id: str) -> None:
        """Remove job status."""
        with self._lock:
            self._statuses.pop(job_id, None)


job_status_store = JobStatusStore()
