import redis
import json
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class Cache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            cls._instance.init_cache()
        return cls._instance

    def init_cache(self):
        try:
            self.client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Cache initialization error: {e}")
            self.client = None

    def get(self, key: str):
        try:
            if not self.client:
                return None
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value, expire=3600):
        try:
            if not self.client:
                return
            self.client.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Cache set error: {e}")


def cached(prefix):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = Cache()
            key = f"{prefix}:{kwargs.get('id', '')}"

            # Try cache first
            result = cache.get(key)
            if result:
                return result

            # Get fresh data
            result = func(*args, **kwargs)
            if result:
                cache.set(key, result)

            return result

        return wrapper

    return decorator