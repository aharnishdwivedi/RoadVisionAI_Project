from typing import Dict, List, Any, Optional
import json
import time
from sqlalchemy.orm import Session
from .database import get_db_session, Stream, StreamResult, Alert
from .logger import vms_logger
from datetime import datetime

class DatabaseStorage:
    def __init__(self):
        pass

    def add_result(self, stream_id: str, result: dict) -> None:
        """Store AI model result in database"""
        start_time = time.time()
        try:
            with get_db_session() as db:
                db_result = StreamResult(
                    stream_id=stream_id,
                    model_name=result.get('model', 'unknown'),
                    timestamp=result.get('timestamp', datetime.now().timestamp()),
                    result_data=json.dumps(result.get('summary', {}))
                )
                db.add(db_result)
                execution_time = time.time() - start_time
                vms_logger.log_database_operation("insert", "stream_results", 1, execution_time)
        except Exception as e:
            vms_logger.log_database_error("insert", str(e), "stream_results")

    def get_results(self, stream_id: str, limit: int = 100) -> List[dict]:
        """Get recent results for a stream"""
        with get_db_session() as db:
            results = db.query(StreamResult).filter(
                StreamResult.stream_id == stream_id
            ).order_by(StreamResult.timestamp.desc()).limit(limit).all()
            
            return [{
                "stream_id": r.stream_id,
                "model": r.model_name,
                "timestamp": r.timestamp,
                "summary": json.loads(r.result_data)
            } for r in results]

    def add_alert(self, alert: dict) -> None:
        """Store alert in database"""
        with get_db_session() as db:
            db_alert = Alert(
                stream_id=alert.get('stream_id', ''),
                alert_type=alert.get('type', 'general'),
                message=alert.get('message', ''),
                severity=alert.get('severity', 'medium')
            )
            db.add(db_alert)

    def get_alerts(self, resolved: Optional[bool] = None) -> List[dict]:
        """Get alerts from database"""
        with get_db_session() as db:
            query = db.query(Alert)
            if resolved is not None:
                query = query.filter(Alert.resolved == resolved)
            
            alerts = query.order_by(Alert.created_at.desc()).limit(100).all()
            
            return [{
                "id": a.id,
                "stream_id": a.stream_id,
                "type": a.alert_type,
                "message": a.message,
                "severity": a.severity,
                "resolved": a.resolved,
                "created_at": a.created_at.isoformat() if a.created_at else None
            } for a in alerts]

    def save_stream_config(self, stream_id: str, source: str, models: List[str]) -> None:
        """Save stream configuration to database"""
        start_time = time.time()
        try:
            with get_db_session() as db:
                # Check if stream exists
                existing = db.query(Stream).filter(Stream.stream_id == stream_id).first()
                if existing:
                    existing.source = source
                    existing.models = json.dumps(models)
                    existing.status = "active"
                    operation = "update"
                else:
                    db_stream = Stream(
                        stream_id=stream_id,
                        source=source,
                        models=json.dumps(models),
                        status="active"
                    )
                    db.add(db_stream)
                    operation = "insert"
                
                execution_time = time.time() - start_time
                vms_logger.log_database_operation(operation, "streams", 1, execution_time)
        except Exception as e:
            vms_logger.log_database_error("save_config", str(e), "streams")

    def update_stream_status(self, stream_id: str, status: str) -> None:
        """Update stream status"""
        with get_db_session() as db:
            stream = db.query(Stream).filter(Stream.stream_id == stream_id).first()
            if stream:
                stream.status = status

    def get_stream_configs(self) -> List[dict]:
        """Get all stream configurations"""
        with get_db_session() as db:
            streams = db.query(Stream).all()
            return [{
                "stream_id": s.stream_id,
                "source": s.source,
                "models": json.loads(s.models),
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None
            } for s in streams]
