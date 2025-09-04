# VMS - Video Management System
## Technical Documentation

### Overview
A lightweight Video Management System capable of handling 10+ video/image inputs with real-time AI model integration for asset detection, defect analysis, road condition monitoring, and traffic analysis.

## System Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: MySQL with SQLAlchemy ORM
- **AI Processing**: Multi-threaded model inference
- **Streaming**: OpenCV-based video processing
- **Logging**: Comprehensive VMS logging system

### Frontend (React + Vite)
- **Framework**: React 18 with Vite
- **Styling**: Modern CSS with gradients and animations
- **API Integration**: REST API communication
- **Real-time Updates**: Polling-based result updates

### Database Schema
```sql
-- Streams table
CREATE TABLE streams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(500) NOT NULL,
    models JSON NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Results table
CREATE TABLE stream_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    timestamp DOUBLE NOT NULL,
    result_data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Components

### 1. Stream Manager (`stream_manager.py`)
- Handles multiple concurrent video streams
- Thread-based processing for scalability
- Supports webcam (0) and video file inputs
- Automatic stream lifecycle management

### 2. Model Manager (`model_manager.py`)
- Integrates 4 AI models:
  - **Asset Detection**: Objects, people, vehicles, barriers
  - **Defect Analysis**: Infrastructure defect scoring
  - **Road Condition**: Surface quality assessment
  - **Traffic Analysis**: Vehicle counting and flow analysis

### 3. Database Storage (`db_storage.py`)
- **Direct SQL storage only** - No in-memory result caching
- All AI model results stored immediately to MySQL database
- Optimized queries with connection pooling and performance logging
- Real-time data persistence for scalability

### 4. API Endpoints (`main.py`)
```python
GET /health                    # System health check
GET /streams                   # List active streams
POST /streams/start           # Start new stream
POST /streams/stop            # Stop stream
GET /results/{stream_id}      # Get AI results
GET /alerts                   # Get active alerts
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- OpenCV compatible system

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure database
mysql -u root -p
CREATE DATABASE road_vision_ai;

# Initialize database
python init_db.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Configuration
Update `backend/app/database.py`:
```python
DATABASE_CONFIG = {
    "username": "your_username",
    "password": "your_password", 
    "database": "road_vision_ai",
    "host": "127.0.0.1",
    "port": 3306
}
```

## Testing Guide

### 1. System Health Test
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","models":["asset_detection","defect_analysis","road_condition","traffic_analysis"]}
```

### 2. Webcam Stream Test
```bash
curl -X POST "http://localhost:8000/streams/start" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "stream_id": "webcam_test",
      "source": "0",
      "models": ["asset_detection", "defect_analysis"]
    }
  }'
```

### 3. Video File Test
```bash
# Place video file in sample_inputs/
curl -X POST "http://localhost:8000/streams/start" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "stream_id": "video_test",
      "source": "/path/to/your/video.mp4",
      "models": ["asset_detection", "defect_analysis", "road_condition", "traffic_analysis"]
    }
  }'
```

### 4. Results Verification
```bash
# Check results
curl "http://localhost:8000/results/video_test?limit=5"

# Check active streams
curl "http://localhost:8000/streams"
```

### 5. Frontend Testing
1. Open http://localhost:5175
2. Start a new stream using the form
3. Click "Refresh Results" to see AI analysis
4. Verify real-time updates every 10 seconds

## Sample Outputs

### Asset Detection Result
```json
{
  "stream_id": "car_video",
  "model": "asset_detection",
  "timestamp": 1756921716.677064,
  "summary": {
    "objects": 2,
    "detections": [
      {
        "x": 93, "y": 262, "width": 50, "height": 50,
        "confidence": 0.9, "class": "person"
      },
      {
        "x": 117, "y": 27, "width": 50, "height": 50,
        "confidence": 0.75, "class": "barrier"
      }
    ],
    "processing_time": 0.13
  }
}
```

### Road Condition Result
```json
{
  "stream_id": "car_video",
  "model": "road_condition",
  "timestamp": 1756921716.4407492,
  "summary": {
    "condition": "excellent",
    "score": 0.853,
    "surface_type": "gravel",
    "weather_impact": "wet",
    "processing_time": 0.114
  }
}
```

## Data Storage Architecture

### Database-Only Storage
- **No In-Memory Caching**: All results stored directly to MySQL database
- **Real-time Persistence**: AI model outputs immediately written to SQL
- **Scalable Design**: Database handles all data persistence and retrieval
- **Data Flow**: Frame → AI Models → Direct SQL Insert → API Retrieval

### Storage Tables
- **stream_results**: All AI model outputs with timestamps
- **streams**: Stream configurations and status
- **alerts**: Generated alerts from AI analysis

## Performance Specifications

### Scalability
- **Concurrent Streams**: 10+ simultaneous video streams
- **Processing**: Multi-threaded AI inference with direct SQL storage
- **Database**: Connection pooling with MySQL for high throughput
- **Memory**: Optimized frame processing with zero result caching

### Response Times
- **API Endpoints**: < 50ms average
- **AI Processing**: 100-200ms per frame
- **Database Inserts**: < 5ms per result
- **Database Queries**: < 10ms average
- **Frontend Updates**: 3-10 second intervals

## File Structure
```
RoadVisionAI_Project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── stream_manager.py    # Stream handling
│   │   ├── model_manager.py     # AI model integration
│   │   ├── database.py          # Database configuration
│   │   ├── db_storage.py        # Data persistence
│   │   └── logger.py            # Logging system
│   ├── requirements.txt         # Python dependencies
│   ├── init_db.py              # Database initialization
│   └── schema.sql              # Database schema
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── App.css             # Styling
│   │   └── api.ts              # API integration
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
├── sample_inputs/              # Test video files
└── models/                     # AI model storage
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Ensure MySQL is running
   brew services start mysql  # macOS
   sudo systemctl start mysql # Linux
   
   # Check credentials in database.py
   ```

2. **Video Stream Not Starting**
   ```bash
   # Check video file path
   ls -la /path/to/video.mp4
   
   # Verify OpenCV installation
   python -c "import cv2; print(cv2.__version__)"
   ```

3. **Frontend Not Loading Results**
   ```bash
   # Check backend is running
   curl http://localhost:8000/health
   
   # Verify CORS settings in main.py
   ```


---

**System Status**: ✅ Fully Functional
**Last Updated**: September 2025
**Version**: 1.0.0
