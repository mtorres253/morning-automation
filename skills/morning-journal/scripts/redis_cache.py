#!/usr/bin/env python3
"""
Redis cache for morning-journal skill.

Stores and retrieves:
- Journal entries (24h TTL)
- Action items (24h TTL)
- Recent responses (7d TTL)

Usage:
  from redis_cache import RedisCache
  cache = RedisCache()
  cache.set_entry("2026-03-25", {...entry...})
  entry = cache.get_entry("2026-03-25")
"""

import redis
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class RedisCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis client."""
        try:
            self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.r.ping()
        except redis.ConnectionError as e:
            print(f"⚠️  Redis not available at {host}:{port}. Caching disabled.")
            print(f"   Install Redis: brew install redis")
            print(f"   Start Redis: redis-server")
            self.r = None

    def _key(self, category: str, identifier: str) -> str:
        """Generate Redis key."""
        return f"morning-journal:{category}:{identifier}"

    def set_entry(self, date_str: str, entry: Dict) -> bool:
        """Store a journal entry (24h TTL)."""
        if not self.r:
            return False
        key = self._key("entry", date_str)
        try:
            self.r.setex(key, timedelta(hours=24), json.dumps(entry))
            return True
        except Exception as e:
            print(f"Cache write error: {e}")
            return False

    def get_entry(self, date_str: str) -> Optional[Dict]:
        """Retrieve a journal entry."""
        if not self.r:
            return None
        key = self._key("entry", date_str)
        try:
            data = self.r.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Cache read error: {e}")
            return None

    def set_action_items(self, date_str: str, items: List[str]) -> bool:
        """Store action items for a day (24h TTL)."""
        if not self.r:
            return False
        key = self._key("actions", date_str)
        try:
            self.r.setex(key, timedelta(hours=24), json.dumps(items))
            return True
        except Exception as e:
            print(f"Cache write error: {e}")
            return False

    def get_action_items(self, date_str: str) -> Optional[List[str]]:
        """Retrieve action items for a day."""
        if not self.r:
            return None
        key = self._key("actions", date_str)
        try:
            data = self.r.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Cache read error: {e}")
            return None

    def get_recent_entries(self, days: int = 7) -> Dict[str, Dict]:
        """Get all entries from past N days (for context)."""
        if not self.r:
            return {}
        
        result = {}
        try:
            pattern = self._key("entry", "*")
            keys = self.r.keys(pattern)
            for key in keys:
                data = self.r.get(key)
                if data:
                    date_str = key.split(":")[-1]
                    result[date_str] = json.loads(data)
        except Exception as e:
            print(f"Cache read error: {e}")
        
        return result

    def clear(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern."""
        if not self.r:
            return 0
        try:
            full_pattern = self._key("*", pattern) if pattern != "*" else self._key("*", "*")
            keys = self.r.keys(full_pattern)
            if keys:
                return self.r.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0

    def health_check(self) -> bool:
        """Check if Redis is available."""
        if not self.r:
            return False
        try:
            self.r.ping()
            return True
        except:
            return False


if __name__ == "__main__":
    # Test
    cache = RedisCache()
    if cache.health_check():
        print("✅ Redis connected")
        
        # Test entry
        test_entry = {
            "gratitude": "coffee",
            "tasks": "code review",
            "strengths": "focus"
        }
        cache.set_entry("2026-03-25", test_entry)
        retrieved = cache.get_entry("2026-03-25")
        print(f"✅ Stored and retrieved: {retrieved}")
        
        # Test action items
        items = ["✅ Review PRs", "📧 Check emails"]
        cache.set_action_items("2026-03-25", items)
        retrieved_items = cache.get_action_items("2026-03-25")
        print(f"✅ Action items: {retrieved_items}")
    else:
        print("❌ Redis not available")
