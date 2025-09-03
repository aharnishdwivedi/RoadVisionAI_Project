import time
import threading
from typing import Dict, Optional, List
import cv2
import numpy as np
from .model_manager import ModelManager
from .db_storage import DatabaseStorage

class StreamWorker(threading.Thread):
    def __init__(self, stream_id: str, source: str, models: List[str], model_mgr: ModelManager, storage: DatabaseStorage, fps: float = 5.0) -> None:
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
        # Handle different source types
        if self.source.isdigit():
            # Webcam source (0, 1, 2, etc.)
            source_int = int(self.source)
            cap = cv2.VideoCapture(source_int)
            # Set webcam properties for better compatibility on macOS
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
        else:
            # File or RTSP source
            cap = cv2.VideoCapture(self.source)
        
        if not cap.isOpened():
            print(f"⚠ Failed to open video source: {self.source}")
            # Fallback to synthetic frames for demo
            while not self._stop_event.is_set():
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                self._process_frame(frame)
                time.sleep(1.0 / self.fps)
            return

        print(f"✓ Successfully opened video source: {self.source}")
        try:
            frame_count = 0
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    if self.source.isdigit():
                        # For webcam, continue trying
                        print(f"⚠ Failed to read from webcam {self.source}, retrying...")
                        time.sleep(0.1)
                        continue
                    else:
                        # For video files, loop back to start
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                
                frame_count += 1
                if frame_count % 30 == 0:  # Log every 30 frames
                    print(f"📹 Processing frame {frame_count} from stream {self.stream_id}")
                
                self._process_frame(frame)
                time.sleep(1.0 / self.fps)
        except Exception as e:
            print(f"❌ Error in stream {self.stream_id}: {e}")
        finally:
            cap.release()
            print(f"🔴 Stream {self.stream_id} stopped")

    def _process_frame(self, frame):
        ts = time.time()
        results = self.model_mgr.run_models(frame, self.models)
        for model_name, summary in results.items():
            result_data = {
                "stream_id": self.stream_id,
                "model": model_name,
                "timestamp": ts,
                "summary": summary,
            }
            self.storage.add_result(self.stream_id, result_data)
            
            # Generate alerts based on results
            self._check_for_alerts(model_name, summary, ts)
    
    def _check_for_alerts(self, model_name: str, summary: dict, timestamp: float):
        """Check model results and generate alerts if needed"""
        try:
            if model_name == "defect_analysis":
                defect_score = summary.get("defect_score", 0)
                if defect_score > 0.7:  # High defect threshold
                    alert = {
                        "stream_id": self.stream_id,
                        "type": "high_defect",
                        "message": f"High defect score detected: {defect_score}",
                        "severity": "high"
                    }
                    self.storage.add_alert(alert)
            
            elif model_name == "asset_detection":
                objects = summary.get("objects", 0)
                if objects > 50:  # Too many objects detected
                    alert = {
                        "stream_id": self.stream_id,
                        "type": "high_object_count",
                        "message": f"High number of objects detected: {objects}",
                        "severity": "medium"
                    }
                    self.storage.add_alert(alert)
        except Exception as e:
            # Log error but don't crash the stream
            pass

class StreamManager:
    def __init__(self, model_mgr: ModelManager, storage: DatabaseStorage) -> None:
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
