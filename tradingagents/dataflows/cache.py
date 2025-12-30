"""
Disk-based caching for API data
"""

import os
import json
import hashlib
import functools
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Optional
from tradingagents.logger_config import get_logger

logger = get_logger(__name__)


class DiskCache:
    """Disk-based cache using JSON files"""

    def __init__(self, cache_dir: str = "dataflows/data_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a unique cache key from function name and arguments"""
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = "|".join(key_parts)

        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{func_name}_{key_hash}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key"""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, func_name: str, args: tuple, kwargs: dict):
        """Get cached value if it exists and is not expired"""
        cache_key = self._make_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)

            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            expiry_time = cached_time + timedelta(hours=self.ttl_hours)

            if datetime.now() > expiry_time:
                logger.debug(f"Cache expired for {func_name} - cached {self.ttl_hours}h ago")
                cache_path.unlink()
                return None

            age = datetime.now() - cached_time
            age_str = f"{age.total_seconds() / 3600:.1f}h ago" if age.total_seconds() >= 3600 else f"{age.total_seconds() / 60:.0f}m ago"
            logger.debug(f"Cache hit for {func_name} - loaded from cache (cached {age_str})")

            return cached_data['value']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Corrupted cache for {func_name} - deleting: {e}")
            cache_path.unlink()
            return None

    def set(self, func_name: str, args: tuple, kwargs: dict, value) -> None:
        """Cache a value to disk"""
        cache_key = self._make_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)

        cached_data = {
            'timestamp': datetime.now().isoformat(),
            'function': func_name,
            'args': str(args),
            'kwargs': str(kwargs),
            'value': value
        }

        try:
            with open(cache_path, 'w') as f:
                json.dump(cached_data, f, indent=2)
            logger.debug(f"Saved {func_name} to disk cache")
        except Exception as e:
            logger.error(f"Cache write failed for {func_name}: {e}")

    def clear_all(self) -> int:
        """Clear all cache files"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        logger.info(f"Cleared cache: deleted {count} cache files")
        return count

    def clear_expired(self) -> int:
        """Clear only expired cache files"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)

                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                expiry_time = cached_time + timedelta(hours=self.ttl_hours)

                if datetime.now() > expiry_time:
                    cache_file.unlink()
                    count += 1
            except Exception:
                cache_file.unlink()
                count += 1

        if count > 0:
            logger.info(f"Cache cleanup: deleted {count} expired cache files")
        return count


_global_cache = None


def get_cache(cache_dir: str = "dataflows/data_cache", ttl_hours: int = 24) -> DiskCache:
    """Get or create the global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = DiskCache(cache_dir=cache_dir, ttl_hours=ttl_hours)
    return _global_cache


def cached(ttl_hours: int = 24, cache_dir: str = "dataflows/data_cache"):
    """Decorator to cache function results to disk"""
    def decorator(func: Callable) -> Callable:
        cache = get_cache(cache_dir=cache_dir, ttl_hours=ttl_hours)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cached_value = cache.get(func.__name__, args, kwargs)
            if cached_value is not None:
                return cached_value

            logger.debug(f"Cache miss for {func.__name__} - fetching from API")
            result = func(*args, **kwargs)

            cache.set(func.__name__, args, kwargs, result)

            return result

        return wrapper
    return decorator
