import time
from typing import Dict, Callable, Any, List
import numpy as np
from ultralytics import YOLO
import os

FakeResult = Dict[str, Any]

class ModelManager:
    def __init__(self) -> None:
        self.model_registry: Dict[str, Callable[[np.ndarray], FakeResult]] = {}
        self.yolo_model = None
        self._load_yolo_model()
        self._register_default_models()
    
    def _load_yolo_model(self) -> None:
        """Load YOLO model for real object detection"""
        try:
            self.yolo_model = YOLO('yolov8n.pt')  # Downloads automatically on first run
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load YOLO model: {e}")
            self.yolo_model = None

    def _register_default_models(self) -> None:
        # Enhanced AI models for VMS
        def asset_detection(frame: np.ndarray) -> FakeResult:
            """Real YOLO object detection"""
            start_time = time.time()
            
            if self.yolo_model is None:
                # Fallback to mock data if YOLO failed to load
                import random
                h, w = frame.shape[:2]
                return {
                    "objects": random.randint(1, 5),
                    "detections": [{
                        "x": random.randint(0, w-50),
                        "y": random.randint(0, h-50),
                        "width": 50, "height": 50,
                        "confidence": round(random.uniform(0.6, 0.95), 2),
                        "class": "mock_object"
                    }],
                    "processing_time": 0.1,
                    "status": "mock_fallback"
                }
            
            try:
                # Run YOLO inference
                results = self.yolo_model(frame, verbose=False)
                
                detections = []
                for r in results:
                    if r.boxes is not None:
                        boxes = r.boxes
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = float(box.conf[0].cpu().numpy())
                            cls = int(box.cls[0].cpu().numpy())
                            
                            # Filter out low confidence detections
                            if conf > 0.3:
                                detections.append({
                                    "x": int(x1),
                                    "y": int(y1),
                                    "width": int(x2 - x1),
                                    "height": int(y2 - y1),
                                    "confidence": round(conf, 2),
                                    "class": self.yolo_model.names[cls]
                                })
                
                processing_time = time.time() - start_time
                
                return {
                    "objects": len(detections),
                    "detections": detections[:10],  # Limit to 10 for display
                    "processing_time": round(processing_time, 3),
                    "status": "yolo_real"
                }
                
            except Exception as e:
                # Fallback on error
                print(f"YOLO inference error: {e}")
                return {
                    "objects": 0,
                    "detections": [],
                    "processing_time": 0.1,
                    "status": "error"
                }

        def defect_analysis(frame: np.ndarray) -> FakeResult:
            mean_val = float(frame.mean())
            base_score = abs(mean_val - 127.5) / 127.5
            
            # Add noise to simulate real analysis
            import random
            noise = random.uniform(-0.1, 0.1)
            defect_score = max(0, min(1, base_score + noise))
            
            # Categorize defects
            defect_type = "none"
            if defect_score > 0.8:
                defect_type = "critical"
            elif defect_score > 0.6:
                defect_type = "major"
            elif defect_score > 0.3:
                defect_type = "minor"
            
            return {
                "defect_score": round(defect_score, 3),
                "defect_type": defect_type,
                "confidence": round(random.uniform(0.7, 0.95), 2),
                "processing_time": round(random.uniform(0.08, 0.20), 3)
            }

        def road_condition(frame: np.ndarray) -> FakeResult:
            """Analyze road surface conditions"""
            import random
            h, w = frame.shape[:2]
            
            # Simulate road condition analysis
            conditions = ["excellent", "good", "fair", "poor", "critical"]
            weights = [0.2, 0.3, 0.3, 0.15, 0.05]  # Probability weights
            condition = random.choices(conditions, weights=weights)[0]
            
            # Generate condition score
            condition_scores = {"excellent": 0.9, "good": 0.75, "fair": 0.6, "poor": 0.4, "critical": 0.2}
            base_score = condition_scores[condition]
            score = base_score + random.uniform(-0.1, 0.1)
            
            return {
                "condition": condition,
                "score": round(max(0, min(1, score)), 3),
                "surface_type": random.choice(["asphalt", "concrete", "gravel", "dirt"]),
                "weather_impact": random.choice(["dry", "wet", "icy", "snowy"]),
                "processing_time": round(random.uniform(0.06, 0.18), 3)
            }

        def traffic_analysis(frame: np.ndarray) -> FakeResult:
            """Analyze traffic density and flow"""
            import random
            
            # Simulate traffic analysis
            vehicle_count = random.randint(0, 25)
            density = "low" if vehicle_count < 5 else "medium" if vehicle_count < 15 else "high"
            
            flow_rate = random.uniform(0.3, 1.0)
            congestion_level = random.uniform(0, 0.8)
            
            return {
                "vehicle_count": vehicle_count,
                "density": density,
                "flow_rate": round(flow_rate, 3),
                "congestion_level": round(congestion_level, 3),
                "average_speed": round(random.uniform(20, 80), 1),
                "processing_time": round(random.uniform(0.10, 0.25), 3)
            }

        # Register all models
        self.model_registry["asset_detection"] = asset_detection
        self.model_registry["defect_analysis"] = defect_analysis
        self.model_registry["road_condition"] = road_condition
        self.model_registry["traffic_analysis"] = traffic_analysis

    def available_models(self) -> List[str]:
        return list(self.model_registry.keys())

    def run_models(self, frame: np.ndarray, models: List[str]) -> Dict[str, FakeResult]:
        results: Dict[str, FakeResult] = {}
        for model_name in models:
            model_fn = self.model_registry.get(model_name)
            if model_fn is None:
                continue
            results[model_name] = model_fn(frame)
        return results
