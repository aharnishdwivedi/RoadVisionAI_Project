from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .schemas import StartStreamRequest, StopStreamRequest
from .model_manager import ModelManager
from .stream_manager import StreamManager
from .db_storage import DatabaseStorage
from .database import create_tables, DB_TYPE
from .logger import vms_logger
import time

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

# Log system startup
vms_logger.log_system_startup(DB_TYPE, model_mgr.available_models())

@app.get("/health")
def health():
    return {"status": "ok", "models": model_mgr.available_models()}

@app.post("/streams/start")
def start_stream(req: StartStreamRequest, request: Request):
    client_ip = request.client.host
    vms_logger.log_api_request("POST", "/streams/start", client_ip)
    vms_logger.log_stream_start(req.config.stream_id, req.config.source, req.config.models)
    
    started = stream_mgr.start_stream(req.config.stream_id, req.config.source, req.config.models)
    if not started:
        vms_logger.log_stream_error(req.config.stream_id, "Stream already running", req.config.source)
        raise HTTPException(status_code=400, detail="Stream already running")
    
    # Save stream configuration to database
    storage.save_stream_config(req.config.stream_id, req.config.source, req.config.models)
    
    # Log scaling metrics
    active_streams = len(stream_mgr.workers)
    vms_logger.log_scaling_metrics(active_streams, active_streams)
    
    return {"ok": True}

@app.post("/streams/stop")
def stop_stream(req: StopStreamRequest, request: Request):
    client_ip = request.client.host
    vms_logger.log_api_request("POST", "/streams/stop", client_ip)
    vms_logger.log_stream_stop(req.stream_id, "user_request")
    
    stopped = stream_mgr.stop_stream(req.stream_id)
    if not stopped:
        vms_logger.log_stream_error(req.stream_id, "Stream not found or already stopped")
        raise HTTPException(status_code=404, detail="Stream not found")
    
    # Update stream status in database
    storage.update_stream_status(req.stream_id, "stopped")
    
    # Log updated scaling metrics
    active_streams = len(stream_mgr.workers)
    vms_logger.log_scaling_metrics(active_streams, active_streams)
    
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
