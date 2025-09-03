# Video Management System (VMS)

Lightweight VMS to manage multiple video/image inputs and run multiple models per stream. Backend uses FastAPI with threads; frontend is a small React dashboard.

## Features
- Multi-input: start 10+ streams (video files, camera index like `0`, or URLs)
- Multiple models per stream: simple stubs (`asset_detection`, `defect_analysis`)
- REST API for control and fetching results
- Minimal dashboard to manage streams and view summaries

## Project structure
```
backend/
  app/
    main.py
    stream_manager.py
    model_manager.py
    storage.py
    schemas.py
  requirements.txt
frontend/
  ... (Vite React app)
```

## Setup

### 1) Backend
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend endpoints:
- GET /health
- GET /streams
- POST /streams/start
- POST /streams/stop
- GET /results/{stream_id}

Start a webcam stream example (macOS often uses `0`):
```
curl -X POST http://localhost:8000/streams/start \
  -H 'Content-Type: application/json' \
  -d '{"config": {"stream_id": "cam0", "source": "0", "models": ["asset_detection","defect_analysis"], "enabled": true}}'
```

### 2) Frontend
```
cd frontend
npm install
npm run dev
```
Set API URL if different:
Create `.env` in `frontend` with:
```
VITE_API_URL=http://localhost:8000
```

Open the dashboard (shown by vite output, usually `http://localhost:5173`).

## Notes
- If a video source cannot be opened, the system generates synthetic frames to keep the pipeline running for demo/testing.
- Results are stored in-memory for simplicity. Replace `InMemoryStorage` with a database for persistence.
- Increase per-stream FPS or number of streams as needed; each stream runs in its own daemon thread.
