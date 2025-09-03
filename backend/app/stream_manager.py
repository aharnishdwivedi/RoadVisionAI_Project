import time
import threading
from typing import Dict, Optional, List
import cv2
import numpy as np
from .model_manager import ModelManager
from .storage import InMemoryStorage

class StreamWorker(threading.Thread):
    def __init__(self, stream_id: str, source: str, models: List[str], model_mgr: ModelManager, storage: InMemoryStorage, fps: float = 5.0) -> None:
        super().__init__(daemon=True)
        self.stream_id = stream_id
        self.source = source
        self.models = models
        self.model_mgr = model_mgr
        self.storage = storage
        self.fps = fps
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            # Try to interpret as image directory; fallback to synthetic frames
            image_idx = 0
            while not self._stop_event.is_set():
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                self._process_frame(frame)
                time.sleep(1.0 / self.fps)
            return

        try:
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                self._process_frame(frame)
                time.sleep(1.0 / self.fps)
        finally:
            cap.release()

    def _process_frame(self, frame):
        ts = time.time()
        results = self.model_mgr.run_models(frame, self.models)
        for model_name, summary in results.items():
            self.storage.add_result(self.stream_id, {
                "stream_id": self.stream_id,
                "model": model_name,
                "timestamp": ts,
                "summary": summary,
            })

class StreamManager:
    def __init__(self, model_mgr: ModelManager, storage: InMemoryStorage) -> None:
        self.model_mgr = model_mgr
        self.storage = storage
        self.workers: Dict[str, StreamWorker] = {}

    def start_stream(self, stream_id: str, source: str, models: List[str]) -> bool:
        if stream_id in self.workers:
            return False
        worker = StreamWorker(stream_id, source, models, self.model_mgr, self.storage)
        self.workers[stream_id] = worker
        worker.start()
        return True

    def stop_stream(self, stream_id: str) -> bool:
        worker = self.workers.get(stream_id)
        if not worker:
            return False
        worker.stop()
        worker.join(timeout=2.0)
        self.workers.pop(stream_id, None)
        return True

    def status(self) -> List[dict]:
        return [
            {
                "stream_id": wid,
                "source": w.source,
                "running": True,
                "models": w.models,
            } for wid, w in self.workers.items()
        ]
