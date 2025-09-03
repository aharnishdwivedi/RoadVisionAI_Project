from typing import Dict, List, Any
from threading import Lock

class InMemoryStorage:
    def __init__(self) -> None:
        self._results: Dict[str, List[dict]] = {}
        self._alerts: List[dict] = []
        self._lock = Lock()

    def add_result(self, stream_id: str, result: dict) -> None:
        with self._lock:
            self._results.setdefault(stream_id, []).append(result)
            if len(self._results[stream_id]) > 5000:
                self._results[stream_id] = self._results[stream_id][-2000:]

    def get_results(self, stream_id: str) -> List[dict]:
        with self._lock:
            return list(self._results.get(stream_id, []))

    def add_alert(self, alert: dict) -> None:
        with self._lock:
            self._alerts.append(alert)
            if len(self._alerts) > 2000:
                self._alerts = self._alerts[-1000:]

    def get_alerts(self) -> List[dict]:
        with self._lock:
            return list(self._alerts)
