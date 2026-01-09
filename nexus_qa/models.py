"""Data models for Nexus CLI Assistant using Pydantic."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Command(BaseModel):
    """Model for saved commands."""
    id: Optional[int] = None
    command: str
    category: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class Category(BaseModel):
    """Model for command categories."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


class HistoryEntry(BaseModel):
    """Model for command history entries."""
    id: Optional[int] = None
    query: str
    response: Optional[str] = None
    provider: Optional[str] = None
    created_at: Optional[datetime] = None


class CacheEntry(BaseModel):
    """Model for cache entries."""
    id: Optional[int] = None
    query_hash: str
    query_text: str
    response: str
    provider: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: datetime


class ProviderConfig(BaseModel):
    """Model for AI provider configuration."""
    api_key: Optional[str] = None
    model: str
    base_url: Optional[str] = None
    rate_limit: Optional[int] = None


class RateLimitingConfig(BaseModel):
    """Model for rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 30
    requests_per_hour: int = 500


class CacheConfig(BaseModel):
    """Model for cache configuration."""
    enabled: bool = True
    ttl_seconds: int = 3600
    max_entries: int = 1000


class Config(BaseModel):
    """Main configuration model."""
    ai_provider: str = "ollama"
    default_model: str = "llama3.2"
    output_mode: str = "brief"
    rate_limiting: RateLimitingConfig = Field(default_factory=RateLimitingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)


class WorkflowStep(BaseModel):
    """Model for a workflow step."""
    name: str
    command: str
    description: Optional[str] = None
    shell: bool = False
    capture_output: bool = True
    continue_on_error: bool = False
    timeout: Optional[int] = 30
    warn_on_output: bool = False
    fail_if_output_contains: Optional[str] = None
    fail_if_empty: bool = False
    fail_if_exit_code_nonzero: bool = False
    alternative: Optional[str] = None
    requires_root: bool = False
    skip_if_no_permission: bool = True


class Workflow(BaseModel):
    """Model for a workflow definition."""
    name: str
    version: str = "1.0.0"
    description: str
    author: Optional[str] = None
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    steps: List[WorkflowStep]
    output_format: str = "summary"  # summary, detailed, json
    estimated_duration: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecution(BaseModel):
    """Model for workflow execution results."""
    id: Optional[int] = None
    workflow_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # running, completed, failed, cancelled
    steps_completed: int = 0
    total_steps: int = 0
    output: Optional[str] = None
    error: Optional[str] = None
