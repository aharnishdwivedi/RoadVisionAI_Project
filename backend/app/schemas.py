from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class StreamConfig(BaseModel):
    stream_id: str
    source: str  # path or rtsp/http
    models: List[str] = []
    enabled: bool = True

class StartStreamRequest(BaseModel):
    config: StreamConfig

class StopStreamRequest(BaseModel):
    stream_id: str

class FrameResult(BaseModel):
    stream_id: str
    model: str
    timestamp: float
    summary: Dict[str, Any]

class Alert(BaseModel):
    stream_id: str
    level: str  # info/warn/critical
    message: str
    timestamp: float

class StreamStatus(BaseModel):
    stream_id: str
    source: str
    running: bool
    models: List[str]
    last_timestamp: Optional[float] = None
