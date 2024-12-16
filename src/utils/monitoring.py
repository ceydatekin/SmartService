from prometheus_client import Counter, Histogram
import functools
import time
import logging

# Metrics
REQUEST_COUNT = Counter('smart_service_requests_total', 'Total requests', ['method'])
REQUEST_LATENCY = Histogram('smart_service_latency_seconds', 'Request latency')

# Logger setup
logger = logging.getLogger('smart_service')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def monitor(method_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            REQUEST_COUNT.labels(method=method_name).inc()
            start_time = time.time()

            try:
                logger.info(f"Starting {method_name}")
                result = func(*args, **kwargs)
                logger.info(f"Completed {method_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {method_name}: {str(e)}")
                raise
            finally:
                REQUEST_LATENCY.observe(time.time() - start_time)

        return wrapper

    return decorator