"""
Logging service that publishes logs to RabbitMQ.
All services use this for centralized logging.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import pika
from pika.exceptions import AMQPConnectionError

# Configure standard Python logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RabbitMQHandler(logging.Handler):
    """Custom logging handler that sends logs to RabbitMQ."""
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 exchange: str = "logs", routing_key: str = "service.logs"):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.routing_key = routing_key
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel = None
    
    def _connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            
            # Declare exchange
            self._channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._connection = None
            self._channel = None
    
    def emit(self, record: logging.LogRecord):
        """Send log record to RabbitMQ."""
        try:
            if self._channel is None or self._channel.is_closed:
                self._connect()
            
            if self._channel is None:
                # Fallback: log locally
                print(f"RABBITMQ LOG: {record.getMessage()}")
                return
            
            # Format log message
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "service": getattr(record, 'service_name', 'unknown'),
                "message": record.getMessage(),
                "logger": record.name,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'user_id'):
                log_entry["user_id"] = record.user_id
            if hasattr(record, 'request_id'):
                log_entry["request_id"] = record.request_id
            
            # Publish to RabbitMQ
            self._channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=json.dumps(log_entry),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
        except Exception as e:
            # Fallback to stderr
            print(f"LOG ERROR: {e} - {record.getMessage()}")
    
    def close(self):
        """Close RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            self._connection.close()


class AsyncRabbitMQHandler(logging.Handler):
    """Async logging handler for non-blocking log publishing."""
    
    def __init__(self, host: str, port: int, username: str, password: str,
                 exchange: str = "logs", routing_key: str = "service.logs"):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.routing_key = routing_key
        self._queue: list = []
        self._connected = False
    
    def emit(self, record: logging.LogRecord):
        """Queue log for async publishing."""
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "service": getattr(record, 'service_name', 'unknown'),
                "message": record.getMessage(),
                "logger": record.name
            }
            
            if hasattr(record, 'user_id'):
                log_entry["user_id"] = record.user_id
            if hasattr(record, 'request_id'):
                log_entry["request_id"] = record.request_id
            
            # Add to queue (in production, use asyncio queue)
            self._queue.append(json.dumps(log_entry))
            
            # Log locally as fallback
            print(f"[LOG] {log_entry['level']}: {log_entry['message']}")
        except Exception as e:
            print(f"LOG ERROR: {e}")


def get_rabbitmq_handler() -> logging.Handler:
    """Get RabbitMQ handler with settings from environment."""
    host = os.environ.get("RABBITMQ_HOST", "localhost")
    port = int(os.environ.get("RABBITMQ_PORT", "5672"))
    username = os.environ.get("RABBITMQ_USER", "guest")
    password = os.environ.get("RABBITMQ_PASSWORD", "guest")
    exchange = os.environ.get("RABBITMQ_LOG_EXCHANGE", "logs")
    routing_key = os.environ.get("RABBITMQ_LOG_ROUTING_KEY", "service.logs")
    
    return RabbitMQHandler(host, port, username, password, exchange, routing_key)


def setup_logging(service_name: str, level: int = logging.INFO):
    """Setup logging for a service with RabbitMQ integration."""
    
    # Create logger
    log = logging.getLogger(service_name)
    log.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    
    # RabbitMQ handler (if available)
    try:
        rabbitmq_handler = get_rabbitmq_handler()
        rabbitmq_handler.setLevel(level)
        log.addHandler(rabbitmq_handler)
        log.info(f"RabbitMQ logging enabled for {service_name}")
    except Exception as e:
        log.warning(f"RabbitMQ logging not available: {e}")
    
    return log


class LogContext:
    """Context manager for adding extra fields to logs."""
    
    def __init__(self, logger: logging.Logger, **kwargs):
        self.logger = logger
        self.extra = kwargs
        self.old_factory = None
    
    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.extra.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)
        return False


def log_request(logger: logging.Logger, method: str, path: str, 
                user_id: Optional[str] = None, request_id: Optional[str] = None):
    """Log an HTTP request."""
    extra = {"request_id": request_id} if request_id else {}
    if user_id:
        extra["user_id"] = user_id
    
    with LogContext(logger, **extra):
        logger.info(f"{method} {path}")


def log_response(logger: logging.Logger, method: str, path: str, 
                  status_code: int, duration_ms: float, user_id: Optional[str] = None):
    """Log an HTTP response."""
    extra = {"user_id": user_id} if user_id else {}
    with LogContext(logger, **extra):
        logger.info(f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)")


def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """Log an error with context."""
    logger.error(
        f"Error: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "error_context": json.dumps(context)
        }
    )