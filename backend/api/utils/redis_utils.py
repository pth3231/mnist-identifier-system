import os
import logging
import json
import redis.asyncio as redis
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Redis connection pool (reused across requests)
_redis_client: Optional[redis.Redis] = None

# Constants
DEFAULT_USER_CACHE_TTL = 1800  # 30 minutes
USER_CACHE_PREFIX = "user:"


async def get_redis() -> redis.Redis:
    """Get or create Redis connection"""
    global _redis_client
    
    if _redis_client is None:
        redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
        _redis_client = await redis.from_url(redis_url, decode_responses=True)
    
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection"""
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


# User data caching
async def set_user_cache(user_id: int, user_data: dict, ttl: int = DEFAULT_USER_CACHE_TTL) -> bool:
    """
    Cache user data by user ID
    
    Args:
        user_id: The user ID
        user_data: Dictionary containing user information
        ttl: Time to live in seconds (default: 30 minutes)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = await get_redis()
        await redis_client.setex(
            f"{USER_CACHE_PREFIX}{user_id}",
            ttl,
            json.dumps(user_data)
        )
        logger.debug(f"User data cached for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to cache user data for user {user_id}: {e}")
        return False


async def get_user_cache(user_id: int) -> Optional[dict]:
    """
    Retrieve cached user data
    
    Args:
        user_id: The user ID
    
    Returns:
        User data dictionary if found, None otherwise
    """
    try:
        redis_client = await get_redis()
        data = await redis_client.get(f"{USER_CACHE_PREFIX}{user_id}")
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve user cache for user {user_id}: {e}")
        return None


async def invalidate_user_cache(user_id: int) -> bool:
    """
    Invalidate user cache
    
    Args:
        user_id: The user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = await get_redis()
        await redis_client.delete(f"{USER_CACHE_PREFIX}{user_id}")
        logger.debug(f"User cache invalidated for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate user cache for user {user_id}: {e}")
        return False


# Generic key-value operations
async def set_key(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set a key-value pair in Redis
    
    Args:
        key: The key
        value: The value
        ttl: Time to live in seconds (None for no expiration)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = await get_redis()
        if ttl:
            await redis_client.setex(key, ttl, str(value))
        else:
            await redis_client.set(key, str(value))
        return True
    except Exception as e:
        logger.error(f"Failed to set key '{key}' in Redis: {e}")
        return False


async def get_key(key: str) -> Optional[str]:
    """
    Get a value from Redis
    
    Args:
        key: The key
    
    Returns:
        Value if key exists, None otherwise
    """
    try:
        redis_client = await get_redis()
        return await redis_client.get(key)
    except Exception as e:
        logger.error(f"Failed to get key '{key}' from Redis: {e}")
        return None


async def delete_key(key: str) -> bool:
    """
    Delete a key from Redis
    
    Args:
        key: The key to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = await get_redis()
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete key '{key}' from Redis: {e}")
        return False


async def check_key_exists(key: str) -> bool:
    """
    Check if a key exists in Redis
    
    Args:
        key: The key
    
    Returns:
        True if key exists, False otherwise
    """
    try:
        redis_client = await get_redis()
        return await redis_client.exists(key) > 0
    except Exception as e:
        logger.error(f"Failed to check key '{key}' in Redis: {e}")
        return False
