"""
Disk-based caching for API data to reduce redundant API calls during development/testing

This module provides a robust caching layer that:
- Saves API responses to disk (JSON format)
- Prevents hitting rate limits during debugging
- Significantly speeds up repeated queries
- Supports TTL (time-to-live) for cache invalidation
"""

import os
import json
import hashlib
import functools
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Callable, Optional


class DiskCache:
    """Simple but robust disk-based cache using JSON files"""

    def __init__(self, cache_dir: str = "dataflows/data_cache", ttl_hours: int = 24):
        """
        Initialize disk cache

        Args:
            cache_dir: Directory to store cache files (relative to project root)
            ttl_hours: Time-to-live in hours (default 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Create a unique cache key from function name and arguments

        Args:
            func_name: Name of the function being cached
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Hash string to use as cache key
        """
        # Create a string representation of the call
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = "|".join(key_parts)

        # Create hash for filename (avoid filesystem issues with special chars)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()

        return f"{func_name}_{key_hash}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key"""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, func_name: str, args: tuple, kwargs: dict) -> Optional[Any]:
        """
        Get cached value if it exists and is not expired

        Args:
            func_name: Name of the function
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Cached value if found and valid, None otherwise
        """
        cache_key = self._make_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            expiry_time = cached_time + timedelta(hours=self.ttl_hours)

            if datetime.now() > expiry_time:
                print(f"CACHE_EXPIRED: {func_name} - cached {self.ttl_hours}h ago")
                cache_path.unlink()  # Delete expired cache
                return None

            # Calculate age
            age = datetime.now() - cached_time
            age_str = f"{age.total_seconds() / 3600:.1f}h ago" if age.total_seconds() >= 3600 else f"{age.total_seconds() / 60:.0f}m ago"
            print(f"CACHE_HIT: {func_name} - loaded from cache (cached {age_str})")

            return cached_data['value']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Corrupted cache file, delete it
            print(f"CACHE_CORRUPT: {func_name} - deleting corrupted cache: {e}")
            cache_path.unlink()
            return None

    def set(self, func_name: str, args: tuple, kwargs: dict, value: Any) -> None:
        """
        Cache a value to disk

        Args:
            func_name: Name of the function
            args: Positional arguments
            kwargs: Keyword arguments
            value: Value to cache
        """
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
            print(f"CACHE_SAVE: {func_name} - saved to disk cache")
        except Exception as e:
            # If caching fails, just log and continue (don't break the actual function)
            print(f"CACHE_WRITE_FAILED: {func_name} - {e}")

    def clear_all(self) -> int:
        """
        Clear all cache files

        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        print(f"CACHE_CLEARED: Deleted {count} cache files")
        return count

    def clear_expired(self) -> int:
        """
        Clear only expired cache files

        Returns:
            Number of files deleted
        """
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
                # If we can't read it, delete it
                cache_file.unlink()
                count += 1

        if count > 0:
            print(f"CACHE_CLEANUP: Deleted {count} expired cache files")
        return count


# Global cache instance
_global_cache = None


def get_cache(cache_dir: str = "dataflows/data_cache", ttl_hours: int = 24) -> DiskCache:
    """
    Get or create the global cache instance

    Args:
        cache_dir: Directory for cache files
        ttl_hours: Time-to-live in hours

    Returns:
        DiskCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = DiskCache(cache_dir=cache_dir, ttl_hours=ttl_hours)
    return _global_cache


def cached(ttl_hours: int = 24, cache_dir: str = "dataflows/data_cache"):
    """
    Decorator to cache function results to disk

    Args:
        ttl_hours: Cache time-to-live in hours (default 24h)
        cache_dir: Directory for cache files

    Usage:
        @cached(ttl_hours=24)
        def route_to_vendor(method, *args, **kwargs):
            # ... expensive API call
            return result

    Example:
        # First call: hits API, caches result
        data = route_to_vendor("get_stock_data", "AAPL", period="1mo")

        # Second call: loads from cache (instant!)
        data = route_to_vendor("get_stock_data", "AAPL", period="1mo")
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache(cache_dir=cache_dir, ttl_hours=ttl_hours)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get from cache
            cached_value = cache.get(func.__name__, args, kwargs)
            if cached_value is not None:
                return cached_value

            # Cache miss - call the actual function
            print(f"CACHE_MISS: {func.__name__} - fetching from API...")
            result = func(*args, **kwargs)

            # Cache the result
            cache.set(func.__name__, args, kwargs, result)

            return result

        return wrapper
    return decorator
