"""Rate limiting for Nexus CLI Assistant."""

import time
from collections import defaultdict
from typing import Optional, Tuple
from nexus_qa.models import RateLimitingConfig


class RateLimiter:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, config: RateLimitingConfig):
        """Initialize rate limiter with configuration."""
        self.config = config
        self.tokens_per_minute = config.requests_per_minute
        self.tokens_per_hour = config.requests_per_hour
        
        # Token buckets: {provider: {minute: tokens, hour: tokens, last_update: time}}
        self.buckets = defaultdict(lambda: {
            "minute": self.tokens_per_minute,
            "hour": self.tokens_per_hour,
            "last_minute_update": time.time(),
            "last_hour_update": time.time(),
        })
    
    def _refill_tokens(self, provider: str):
        """Refill tokens based on elapsed time."""
        bucket = self.buckets[provider]
        now = time.time()
        
        # Refill minute bucket
        elapsed_minutes = (now - bucket["last_minute_update"]) / 60
        if elapsed_minutes >= 1:
            bucket["minute"] = self.tokens_per_minute
            bucket["last_minute_update"] = now
        elif elapsed_minutes > 0:
            # Partial refill
            tokens_to_add = int(elapsed_minutes * self.tokens_per_minute)
            bucket["minute"] = min(self.tokens_per_minute, bucket["minute"] + tokens_to_add)
        
        # Refill hour bucket
        elapsed_hours = (now - bucket["last_hour_update"]) / 3600
        if elapsed_hours >= 1:
            bucket["hour"] = self.tokens_per_hour
            bucket["last_hour_update"] = now
        elif elapsed_hours > 0:
            # Partial refill
            tokens_to_add = int(elapsed_hours * self.tokens_per_hour)
            bucket["hour"] = min(self.tokens_per_hour, bucket["hour"] + tokens_to_add)
    
    def is_allowed(self, provider: str) -> Tuple[bool, Optional[str]]:
        """Check if request is allowed for provider."""
        if not self.config.enabled:
            return True, None
        
        self._refill_tokens(provider)
        bucket = self.buckets[provider]
        
        # Check both minute and hour limits
        if bucket["minute"] <= 0:
            wait_time = 60 - (time.time() - bucket["last_minute_update"])
            return False, f"Rate limit exceeded. Try again in {int(wait_time)} seconds."
        
        if bucket["hour"] <= 0:
            wait_time = 3600 - (time.time() - bucket["last_hour_update"])
            return False, f"Hourly rate limit exceeded. Try again in {int(wait_time / 60)} minutes."
        
        # Consume tokens
        bucket["minute"] -= 1
        bucket["hour"] -= 1
        
        return True, None
    
    def get_status(self, provider: str) -> dict:
        """Get rate limit status for provider."""
        self._refill_tokens(provider)
        bucket = self.buckets[provider]
        
        return {
            "minute_tokens": bucket["minute"],
            "hour_tokens": bucket["hour"],
            "minute_limit": self.tokens_per_minute,
            "hour_limit": self.tokens_per_hour,
        }

