from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import StartStreamRequest, StopStreamRequest
from .model_manager import ModelManager
from .stream_manager import StreamManager
from .storage import InMemoryStorage

app = FastAPI(title="VMS Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_mgr = ModelManager()
storage = InMemoryStorage()
stream_mgr = StreamManager(model_mgr, storage)

@app.get("/health")
def health():
    return {"status": "ok", "models": model_mgr.available_models()}

@app.post("/streams/start")
def start_stream(req: StartStreamRequest):
    started = stream_mgr.start_stream(req.config.stream_id, req.config.source, req.config.models)
    if not started:
        raise HTTPException(status_code=400, detail="Stream already running")
    return {"ok": True}

@app.post("/streams/stop")
def stop_stream(req: StopStreamRequest):
    stopped = stream_mgr.stop_stream(req.stream_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="Stream not found")
    return {"ok": True}

@app.get("/streams")
def list_streams():
    return {"streams": stream_mgr.status()}

@app.get("/results/{stream_id}")
def get_results(stream_id: str):
    return {"results": storage.get_results(stream_id)}
