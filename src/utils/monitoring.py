import logging
from prometheus_client import Counter, Histogram, start_http_server
import functools
import time
from typing import Optional, Callable
import threading
import asyncio

# Metrics
REQUEST_COUNT = Counter(
    'smart_service_requests_total',
    'Total requests',
    ['method', 'status']
)

REQUEST_LATENCY = Histogram(
    'smart_service_request_latency_seconds',
    'Request latency in seconds',
    ['method']
)

# Logger setup
logger = logging.getLogger(__name__)

def monitor(method_name: Optional[str] = None) -> Callable:
    """Monitoring decorator for tracking metrics"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                REQUEST_COUNT.labels(
                    method=method_name or func.__name__,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                REQUEST_COUNT.labels(
                    method=method_name or func.__name__,
                    status="error"
                ).inc()
                raise e
            finally:
                REQUEST_LATENCY.labels(
                    method=method_name or func.__name__
                ).observe(time.time() - start_time)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                REQUEST_COUNT.labels(
                    method=method_name or func.__name__,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                REQUEST_COUNT.labels(
                    method=method_name or func.__name__,
                    status="error"
                ).inc()
                raise e
            finally:
                REQUEST_LATENCY.labels(
                    method=method_name or func.__name__
                ).observe(time.time() - start_time)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class MetricsServer:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.is_running = False
        return cls._instance

    def start(self, port: int = 8000) -> bool:
        if not self.is_running:
            try:
                start_http_server(port)
                self.is_running = True
                logger.info(f"Metrics server started on port {port}")
                return True
            except Exception as e:
                logger.error(f"Failed to start metrics server: {e}")
                return False
        return True

    def get_metrics(self) -> dict:
        return {
            'total_requests': REQUEST_COUNT._value.sum(),
            'average_latency': REQUEST_LATENCY._sum.sum() / REQUEST_LATENCY._count.sum()
            if REQUEST_LATENCY._count.sum() > 0 else 0
        }