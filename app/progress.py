from __future__ import annotations

import queue
import threading
from typing import Dict, List, Optional, Set


class ProgressStream:
    """Thread-safe publish/subscribe stream for SSE progress updates."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[queue.Queue[Optional[str]]]] = {}
        self._lock = threading.Lock()
        self._closed_sessions: Set[str] = set()

    def register(self, session_id: str) -> queue.Queue[Optional[str]]:
        """Register a new listener queue for the given session."""
        listener_queue: queue.Queue[Optional[str]] = queue.Queue()
        with self._lock:
            if session_id in self._closed_sessions:
                listener_queue.put(None)
                return listener_queue
            listeners = self._listeners.setdefault(session_id, [])
            listeners.append(listener_queue)
        return listener_queue

    def unregister(
        self, session_id: str, listener_queue: queue.Queue[Optional[str]]
    ) -> None:
        """Remove a listener queue for the given session."""
        with self._lock:
            listeners = self._listeners.get(session_id)
            if not listeners:
                return
            if listener_queue in listeners:
                listeners.remove(listener_queue)
            if not listeners:
                self._listeners.pop(session_id, None)

    def publish(self, session_id: str, message: str) -> None:
        """Publish a message to all listeners of the session."""
        with self._lock:
            self._closed_sessions.discard(session_id)
            listeners = list(self._listeners.get(session_id, []))
        for listener in listeners:
            listener.put(message)

    def close(self, session_id: str) -> None:
        """Signal completion to all listeners of the session."""
        with self._lock:
            listeners = self._listeners.pop(session_id, [])
            self._closed_sessions.add(session_id)
        for listener in listeners:
            listener.put(None)


progress_stream = ProgressStream()
