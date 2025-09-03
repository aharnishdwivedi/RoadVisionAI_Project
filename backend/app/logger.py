import logging
import sys
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, Optional

class VMSLogger:
    """Centralized logging system for Video Management System"""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging with multiple handlers"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_dir / "vms.log"),
                logging.FileHandler(log_dir / "vms_error.log", mode='a')
            ]
        )
        
        # Create specialized loggers
        self.main_logger = logging.getLogger("VMS.Main")
        self.stream_logger = logging.getLogger("VMS.Stream")
        self.model_logger = logging.getLogger("VMS.Model")
        self.db_logger = logging.getLogger("VMS.Database")
        self.api_logger = logging.getLogger("VMS.API")
        
        # Set error handler to only log errors
        error_handler = logging.FileHandler(log_dir / "vms_error.log")
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter('%(asctime)s - %(name)s - ERROR - %(message)s')
        error_handler.setFormatter(error_formatter)
        
        for logger in [self.main_logger, self.stream_logger, self.model_logger, self.db_logger, self.api_logger]:
            logger.addHandler(error_handler)
    
    def log_system_startup(self, db_type: str, models: list):
        """Log system initialization"""
        self.main_logger.info("🚀 VMS System Starting Up")
        self.main_logger.info(f"📊 Database Type: {db_type}")
        self.main_logger.info(f"🤖 Available AI Models: {', '.join(models)}")
        self.main_logger.info("✅ System Ready for Stream Processing")
    
    def log_stream_start(self, stream_id: str, source: str, models: list):
        """Log stream start event"""
        self.stream_logger.info(f"🎬 Starting stream '{stream_id}' from source '{source}'")
        self.stream_logger.info(f"🔧 Models enabled: {', '.join(models)}")
    
    def log_stream_stop(self, stream_id: str, reason: str = "user_request"):
        """Log stream stop event"""
        self.stream_logger.info(f"🛑 Stopping stream '{stream_id}' - Reason: {reason}")
    
    def log_stream_error(self, stream_id: str, error: str, source: str = None):
        """Log stream errors"""
        msg = f"❌ Stream '{stream_id}' error: {error}"
        if source:
            msg += f" (source: {source})"
        self.stream_logger.error(msg)
    
    def log_stream_success(self, stream_id: str, source: str):
        """Log successful stream connection"""
        self.stream_logger.info(f"✅ Stream '{stream_id}' connected successfully to source '{source}'")
    
    def log_frame_processing(self, stream_id: str, frame_count: int, models_used: list, processing_time: float):
        """Log frame processing metrics"""
        self.stream_logger.debug(f"📹 Stream '{stream_id}' - Frame {frame_count} processed in {processing_time:.3f}s using {len(models_used)} models")
    
    def log_model_inference(self, stream_id: str, model_name: str, processing_time: float, result_summary: Dict[str, Any]):
        """Log AI model inference results"""
        self.model_logger.debug(f"🧠 Model '{model_name}' on stream '{stream_id}' - {processing_time:.3f}s - {json.dumps(result_summary, default=str)}")
    
    def log_model_performance(self, model_name: str, avg_time: float, total_inferences: int):
        """Log model performance metrics"""
        self.model_logger.info(f"📊 Model '{model_name}' performance - Avg: {avg_time:.3f}s, Total inferences: {total_inferences}")
    
    def log_database_operation(self, operation: str, table: str, record_count: int = 1, execution_time: float = None):
        """Log database operations"""
        msg = f"💾 DB {operation.upper()} - Table: {table}, Records: {record_count}"
        if execution_time:
            msg += f", Time: {execution_time:.3f}s"
        self.db_logger.debug(msg)
    
    def log_database_error(self, operation: str, error: str, table: str = None):
        """Log database errors"""
        msg = f"❌ DB Error during {operation}: {error}"
        if table:
            msg += f" (table: {table})"
        self.db_logger.error(msg)
    
    def log_api_request(self, method: str, endpoint: str, client_ip: str = None):
        """Log API requests"""
        msg = f"🌐 API {method} {endpoint}"
        if client_ip:
            msg += f" from {client_ip}"
        self.api_logger.info(msg)
    
    def log_scaling_metrics(self, active_streams: int, total_threads: int, memory_usage: Optional[float] = None):
        """Log system scaling metrics"""
        msg = f"📈 Scaling Metrics - Active Streams: {active_streams}, Threads: {total_threads}"
        if memory_usage:
            msg += f", Memory: {memory_usage:.1f}MB"
        self.main_logger.info(msg)
    
    def log_alert_generated(self, stream_id: str, alert_type: str, severity: str, message: str):
        """Log alert generation"""
        self.main_logger.warning(f"🚨 ALERT [{severity.upper()}] - Stream '{stream_id}' - {alert_type}: {message}")
    
    def log_concurrent_processing(self, stream_id: str, concurrent_count: int, queue_size: int = None):
        """Log concurrent processing status"""
        msg = f"⚡ Stream '{stream_id}' - Concurrent processes: {concurrent_count}"
        if queue_size is not None:
            msg += f", Queue size: {queue_size}"
        self.stream_logger.debug(msg)

# Global logger instance
vms_logger = VMSLogger()
