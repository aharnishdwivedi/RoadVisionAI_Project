import time
from typing import Dict, Callable, Any, List
import numpy as np

FakeResult = Dict[str, Any]

class ModelManager:
    def __init__(self) -> None:
        self.model_registry: Dict[str, Callable[[np.ndarray], FakeResult]] = {}
        self._register_default_models()

    def _register_default_models(self) -> None:
        # Enhanced AI models for VMS
        def asset_detection(frame: np.ndarray) -> FakeResult:
            h, w = frame.shape[:2]
            # Simulate more realistic object detection
            base_objects = max(1, (h * w) // 200000)
            # Add some randomness to simulate real detection
            import random
            variation = random.randint(-2, 5)
            objects = max(0, base_objects + variation)
            
            # Simulate bounding boxes
            boxes = []
            for i in range(min(objects, 10)):  # Limit to 10 for display
                x = random.randint(0, w-50)
                y = random.randint(0, h-50)
                boxes.append({
                    "x": x, "y": y, "width": 50, "height": 50,
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "class": random.choice(["vehicle", "person", "sign", "barrier"])
                })
            
            return {
                "objects": objects,
                "detections": boxes,
                "processing_time": round(random.uniform(0.05, 0.15), 3)
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
