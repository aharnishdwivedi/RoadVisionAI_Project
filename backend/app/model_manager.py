import time
from typing import Dict, Callable, Any, List
import numpy as np

FakeResult = Dict[str, Any]

class ModelManager:
    def __init__(self) -> None:
        self.model_registry: Dict[str, Callable[[np.ndarray], FakeResult]] = {}
        self._register_default_models()

    def _register_default_models(self) -> None:
        # Simple stub models
        def asset_detection(frame: np.ndarray) -> FakeResult:
            h, w = frame.shape[:2]
            return {"objects": max(1, (h * w) // 200000)}

        def defect_analysis(frame: np.ndarray) -> FakeResult:
            mean_val = float(frame.mean())
            return {"defect_score": round(abs(mean_val - 127.5) / 127.5, 3)}

        self.model_registry["asset_detection"] = asset_detection
        self.model_registry["defect_analysis"] = defect_analysis

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
