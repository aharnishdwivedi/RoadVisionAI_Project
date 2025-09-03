#!/bin/bash

# Test video stream with VMS
# Replace 'your_video.mp4' with your actual video filename

VIDEO_PATH="/Users/aharnishdwivedi/Desktop/RoadVisionAI_Project/sample_inputs/car.mp4.mp4"

curl -X POST "http://localhost:8000/streams/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"config\": {
      \"stream_id\": \"video_test\",
      \"source\": \"$VIDEO_PATH\",
      \"models\": [\"asset_detection\", \"defect_analysis\", \"road_condition\", \"traffic_analysis\"]
    }
  }"

echo "Video stream started! Check frontend at http://localhost:5175"
