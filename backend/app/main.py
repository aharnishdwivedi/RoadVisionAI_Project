from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import StartStreamRequest, StopStreamRequest
from .model_manager import ModelManager
from .stream_manager import StreamManager
from .db_storage import DatabaseStorage
from .database import create_tables

app = FastAPI(title="VMS Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
create_tables()

model_mgr = ModelManager()
storage = DatabaseStorage()
stream_mgr = StreamManager(model_mgr, storage)

@app.get("/health")
def health():
    return {"status": "ok", "models": model_mgr.available_models()}

@app.post("/streams/start")
def start_stream(req: StartStreamRequest):
    started = stream_mgr.start_stream(req.config.stream_id, req.config.source, req.config.models)
    if not started:
        raise HTTPException(status_code=400, detail="Stream already running")
    # Save stream configuration to database
    storage.save_stream_config(req.config.stream_id, req.config.source, req.config.models)
    return {"ok": True}

@app.post("/streams/stop")
def stop_stream(req: StopStreamRequest):
    stopped = stream_mgr.stop_stream(req.stream_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="Stream not found")
    # Update stream status in database
    storage.update_stream_status(req.stream_id, "stopped")
    return {"ok": True}

@app.get("/streams")
def list_streams():
    return {"streams": stream_mgr.status()}

@app.get("/results/{stream_id}")
def get_results(stream_id: str):
    return {"results": storage.get_results(stream_id)}

@app.get("/alerts")
def get_alerts():
    return {"alerts": storage.get_alerts(resolved=False)}

@app.get("/alerts/all")
def get_all_alerts():
    return {"alerts": storage.get_alerts()}
