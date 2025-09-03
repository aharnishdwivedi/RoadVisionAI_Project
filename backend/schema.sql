-- Video Management System Database Schema
-- MySQL Database: road_vision_ai

CREATE DATABASE IF NOT EXISTS road_vision_ai;
USE road_vision_ai;

-- Streams table to store video stream configurations
CREATE TABLE IF NOT EXISTS streams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL UNIQUE,
    source VARCHAR(500) NOT NULL,
    models TEXT NOT NULL COMMENT 'JSON array of model names',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stream_id (stream_id),
    INDEX idx_status (status)
);

-- Stream results table to store AI model inference results
CREATE TABLE IF NOT EXISTS stream_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    timestamp DOUBLE NOT NULL,
    result_data TEXT NOT NULL COMMENT 'JSON string of model results',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stream_id (stream_id),
    INDEX idx_model_name (model_name),
    INDEX idx_timestamp (timestamp),
    INDEX idx_created_at (created_at)
);

-- Alerts table to store system alerts and notifications
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(50) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    INDEX idx_stream_id (stream_id),
    INDEX idx_alert_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved),
    INDEX idx_created_at (created_at)
);

-- Insert sample data for testing
INSERT IGNORE INTO streams (stream_id, source, models, status) VALUES
('demo_stream_1', '0', '["asset_detection", "defect_analysis"]', 'active'),
('demo_stream_2', 'sample_video.mp4', '["road_condition", "traffic_analysis"]', 'active');

-- Create user for application (optional, adjust credentials as needed)
-- CREATE USER IF NOT EXISTS 'vms_user'@'localhost' IDENTIFIED BY 'vms_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON road_vision_ai.* TO 'vms_user'@'localhost';
-- FLUSH PRIVILEGES;
