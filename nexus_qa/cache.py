"""Caching system for Nexus CLI Assistant."""

import hashlib
from datetime import datetime, timedelta
from typing import Optional
from nexus_qa.models import CacheEntry, CacheConfig
from nexus_qa.storage import Storage


class Cache:
    """Cache manager for query responses."""
    
    def __init__(self, storage: Storage, config: CacheConfig):
        """Initialize cache with storage and configuration."""
        self.storage = storage
        self.config = config
        self.hits = 0
        self.misses = 0
    
    def _hash_query(self, query: str, provider: Optional[str] = None) -> str:
        """Generate hash for query."""
        query_str = f"{provider}:{query}" if provider else query
        return hashlib.sha256(query_str.encode()).hexdigest()
    
    def get(self, query: str, provider: Optional[str] = None) -> Optional[str]:
        """Get cached response for query."""
        if not self.config.enabled:
            return None
        
        query_hash = self._hash_query(query, provider)
        cache_entry = self.storage.get_cache(query_hash)
        
        if cache_entry:
            self.hits += 1
            return cache_entry.response
        else:
            self.misses += 1
            return None
    
    def set(self, query: str, response: str, provider: Optional[str] = None):
        """Cache a query response."""
        if not self.config.enabled:
            return
        
        # Cleanup expired entries periodically
        if self.storage.get_cache_count() > self.config.max_entries:
            self.storage.cleanup_expired_cache()
        
        query_hash = self._hash_query(query, provider)
        expires_at = datetime.now() + timedelta(seconds=self.config.ttl_seconds)
        
        self.storage.save_cache(query_hash, query, response, provider, expires_at)
    
    def clear(self):
        """Clear all cache entries."""
        # We'll implement this by deleting all entries
        # For now, we'll just cleanup expired ones
        self.storage.cleanup_expired_cache()
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_entries": self.storage.get_cache_count(),
        }

