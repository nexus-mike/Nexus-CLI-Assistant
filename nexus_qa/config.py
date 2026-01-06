"""Configuration management for Nexus CLI Assistant."""

import os
import re
from pathlib import Path
from typing import Optional
import yaml
from nexus_qa.models import Config, ProviderConfig, RateLimitingConfig, CacheConfig


def expand_env_vars(value: str) -> str:
    """Expand environment variables in string values."""
    if not isinstance(value, str):
        return value
    
    def replace_env(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))
    
    return re.sub(r'\$\{([^}]+)\}', replace_env, value)


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        config_dir = Path.home() / ".config" / "nexus"
        config_path = config_dir / "config.yaml"
    
    # Create default config if file doesn't exist
    if not config_path.exists():
        return _create_default_config(config_path)
    
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f) or {}
    
    # Expand environment variables
    config_data = _expand_env_in_dict(config_data)
    
    # Parse rate limiting config
    rate_limiting_data = config_data.get("rate_limiting", {})
    rate_limiting = RateLimitingConfig(**rate_limiting_data)
    
    # Parse cache config
    cache_data = config_data.get("cache", {})
    cache = CacheConfig(**cache_data)
    
    # Parse providers
    providers = {}
    providers_data = config_data.get("providers", {})
    for provider_name, provider_data in providers_data.items():
        # Expand API keys from environment
        if "api_key" in provider_data:
            provider_data["api_key"] = expand_env_vars(provider_data["api_key"])
        providers[provider_name] = ProviderConfig(**provider_data)
    
    return Config(
        ai_provider=config_data.get("ai_provider", "ollama"),
        default_model=config_data.get("default_model", "llama3.2"),
        output_mode=config_data.get("output_mode", "brief"),
        rate_limiting=rate_limiting,
        cache=cache,
        providers=providers,
    )


def _expand_env_in_dict(data: dict) -> dict:
    """Recursively expand environment variables in dictionary."""
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _expand_env_in_dict(value)
        elif isinstance(value, str):
            result[key] = expand_env_vars(value)
        else:
            result[key] = value
    return result


def _create_default_config(config_path: Path) -> Config:
    """Create default configuration file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Try to copy from example if it exists
    example_path = Path(__file__).parent.parent / "config" / "config.yaml.example"
    if example_path.exists():
        import shutil
        shutil.copy(example_path, config_path)
        return load_config(config_path)
    
    # Otherwise create minimal default
    default_config = {
        "ai_provider": "ollama",
        "default_model": "llama3.2",
        "output_mode": "brief",
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 30,
            "requests_per_hour": 500,
        },
        "cache": {
            "enabled": True,
            "ttl_seconds": 3600,
            "max_entries": 1000,
        },
        "providers": {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "llama3.2",
            },
        },
    }
    
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    return load_config(config_path)


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return Path.home() / ".config" / "nexus" / "config.yaml"

