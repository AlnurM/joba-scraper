import json
import time
from redis import Redis
from redis.exceptions import RedisError
from loguru import logger

from src.config import settings


class RedisService:
    """Service for interacting with Redis cache."""

    def __init__(self):
        self.redis = None
        self.connected = False

    def connect(self):
        """Connect to Redis server."""
        try:
            self.redis = Redis.from_url(
                settings.REDIS_URI,
                decode_responses=True
            )
            # Check connection
            self.redis.ping()
            self.connected = True
            logger.info("Successfully connected to Redis")
            return True
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            self.connected = False
            return False

    def set_cache(self, key, value, expiry=3600):
        """Set a value in the cache with expiry in seconds."""
        if not self.connected:
            logger.warning("Redis not connected. Cannot set cache.")
            return False

        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self.redis.set(key, value, ex=expiry)
            logger.debug(f"Set cache for key: {key} with expiry: {expiry}s")
            return True
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {str(e)}")
            return False

    def get_cache(self, key):
        """Get a value from the cache."""
        if not self.connected:
            logger.warning("Redis not connected. Cannot get cache.")
            return None

        try:
            value = self.redis.get(key)
            if value is None:
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            try:
                # Try to parse as JSON
                return json.loads(value)
            except json.JSONDecodeError:
                # Return as is if not JSON
                return value
        except Exception as e:
            logger.error(f"Error getting cache for key {key}: {str(e)}")
            return None

    def delete_cache(self, key):
        """Delete a value from the cache."""
        if not self.connected:
            logger.warning("Redis not connected. Cannot delete cache.")
            return False

        try:
            result = self.redis.delete(key)
            if result:
                logger.debug(f"Deleted cache for key: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {str(e)}")
            return False

    def rate_limit(self, key, limit=60, period=60):
        """
        Implement rate limiting using Redis.
        Returns True if the request is allowed, False if rate limited.
        """
        if not self.connected:
            logger.warning("Redis not connected. Cannot apply rate limiting.")
            return True  # Allow the request if Redis is not available

        try:
            current_time = int(time.time())
            # Remove counts older than the period
            self.redis.zremrangebyscore(key, 0, current_time - period)
            
            # Count current requests in the period
            current_count = self.redis.zcard(key)
            
            if current_count >= limit:
                logger.warning(f"Rate limit exceeded for {key}: {current_count}/{limit} in {period}s")
                return False
            
            # Add current request to the sorted set
            self.redis.zadd(key, {str(current_time): current_time})
            # Set expiry on the key
            self.redis.expire(key, period)
            
            return True
        except Exception as e:
            logger.error(f"Error in rate limiting for key {key}: {str(e)}")
            return True  # Allow the request if there's an error

    def close(self):
        """Close the Redis connection."""
        if self.redis:
            try:
                self.redis.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {str(e)}")


# Singleton instance
redis_service = RedisService()