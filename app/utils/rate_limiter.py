import os
import logging
import redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

logger = logging.getLogger("hospital.limiter")

# Attempt Redis connection, fallback to memory storage if Redis is down/unavailable
storage_uri = "memory://"
if not os.environ.get("VERCEL") and settings.REDIS_URL and "redis" in settings.REDIS_URL:
    try:
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.5)
        r.ping()
        storage_uri = settings.REDIS_URL
        logger.info("Rate limiter connected to Redis.")
    except Exception as e:
        logger.warning(f"Redis unavailable for rate limiter ({e}). Falling back to memory storage.")
        storage_uri = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_STANDARD],
    storage_uri=storage_uri,
)
