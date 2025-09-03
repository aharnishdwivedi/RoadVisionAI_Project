#!/usr/bin/env python3
"""
Database initialization script for VMS
Run this to create tables and setup initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, get_db_session, Stream
import json

def init_database():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    create_tables()
    print("✓ Tables created successfully")
    
    # Add sample streams
    print("Adding sample data...")
    with get_db_session() as db:
        # Check if sample data already exists
        existing = db.query(Stream).filter(Stream.stream_id == 'demo_stream_1').first()
        if not existing:
            sample_streams = [
                Stream(
                    stream_id='demo_stream_1',
                    source='0',  # Webcam
                    models=json.dumps(['asset_detection', 'defect_analysis']),
                    status='stopped'
                ),
                Stream(
                    stream_id='demo_stream_2', 
                    source='sample_video.mp4',
                    models=json.dumps(['road_condition', 'traffic_analysis']),
                    status='stopped'
                )
            ]
            
            for stream in sample_streams:
                db.add(stream)
            
            print("✓ Sample data added")
        else:
            print("✓ Sample data already exists")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()
