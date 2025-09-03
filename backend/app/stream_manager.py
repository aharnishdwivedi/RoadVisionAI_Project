import time
import threading
from typing import Dict, Optional, List
import cv2
import numpy as np
from .model_manager import ModelManager
from .db_storage import DatabaseStorage
from .logger import vms_logger

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
            vms_logger.log_stream_error(self.stream_id, f"Failed to open video source: {self.source}", self.source)
            # Fallback to synthetic frames for demo
            vms_logger.log_stream_start(self.stream_id, "synthetic_fallback", self.models)
            while not self._stop_event.is_set():
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                self._process_frame(frame)
                time.sleep(1.0 / self.fps)
            return

        vms_logger.log_stream_success(self.stream_id, self.source)
        try:
            frame_count = 0
            start_time = time.time()
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    if self.source.isdigit():
                        # For webcam, continue trying
                        vms_logger.log_stream_error(self.stream_id, f"Failed to read from webcam, retrying...", self.source)
                        time.sleep(0.1)
                        continue
                    else:
                        # For video files, loop back to start
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                
                frame_count += 1
                
                # Process frame and measure time
                frame_start = time.time()
                self._process_frame(frame)
                frame_time = time.time() - frame_start
                
                # Log frame processing metrics every 30 frames
                if frame_count % 30 == 0:
                    vms_logger.log_frame_processing(self.stream_id, frame_count, self.models, frame_time)
                    
                    # Log concurrent processing status
                    active_threads = threading.active_count()
                    vms_logger.log_concurrent_processing(self.stream_id, active_threads)
                
                time.sleep(1.0 / self.fps)
        except Exception as e:
            vms_logger.log_stream_error(self.stream_id, f"Runtime error: {str(e)}", self.source)
        finally:
            cap.release()
            runtime = time.time() - start_time
            vms_logger.log_stream_stop(self.stream_id, f"completed_after_{runtime:.1f}s")

    def _process_frame(self, frame):
        ts = time.time()
        results = self.model_mgr.run_models(frame, self.models)
        
        for model_name, summary in results.items():
            # Log model inference
            processing_time = summary.get('processing_time', 0)
            vms_logger.log_model_inference(self.stream_id, model_name, processing_time, summary)
            
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
                    vms_logger.log_alert_generated(self.stream_id, "high_defect", "high", f"Defect score: {defect_score}")
            
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
                    vms_logger.log_alert_generated(self.stream_id, "high_object_count", "medium", f"Object count: {objects}")
            
            elif model_name == "road_condition":
                condition = summary.get("condition", "unknown")
                if condition in ["poor", "critical"]:
                    alert = {
                        "stream_id": self.stream_id,
                        "type": "poor_road_condition",
                        "message": f"Poor road condition detected: {condition}",
                        "severity": "high" if condition == "critical" else "medium"
                    }
                    self.storage.add_alert(alert)
                    vms_logger.log_alert_generated(self.stream_id, "poor_road_condition", alert["severity"], f"Condition: {condition}")
            
            elif model_name == "traffic_analysis":
                congestion = summary.get("congestion_level", 0)
                if congestion > 0.8:  # High congestion
                    alert = {
                        "stream_id": self.stream_id,
                        "type": "high_traffic_congestion",
                        "message": f"High traffic congestion detected: {congestion:.2f}",
                        "severity": "medium"
                    }
                    self.storage.add_alert(alert)
                    vms_logger.log_alert_generated(self.stream_id, "high_traffic_congestion", "medium", f"Congestion level: {congestion:.2f}")
                    
        except Exception as e:
            vms_logger.log_stream_error(self.stream_id, f"Alert generation error: {str(e)}")

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
