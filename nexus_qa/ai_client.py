"""AI client abstraction for multiple providers."""

import os
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import requests
from nexus_qa.models import ProviderConfig
from nexus_qa.rate_limiter import RateLimiter
from nexus_qa.cache import Cache


class AIClient(ABC):
    """Abstract base class for AI clients."""
    
    def __init__(self, config: ProviderConfig, rate_limiter: Optional[RateLimiter] = None, 
                 cache: Optional[Cache] = None):
        """Initialize AI client."""
        self.config = config
        self.rate_limiter = rate_limiter
        self.cache = cache
    
    @abstractmethod
    def ask(self, question: str, verbose: bool = False) -> str:
        """Ask a question and get a response."""
        pass
    
    def _check_cache(self, question: str) -> Optional[str]:
        """Check cache for question."""
        if self.cache:
            return self.cache.get(question, self.__class__.__name__)
        return None
    
    def _save_cache(self, question: str, response: str):
        """Save response to cache."""
        if self.cache:
            self.cache.set(question, response, self.__class__.__name__)
    
    def _check_rate_limit(self) -> Tuple[bool, Optional[str]]:
        """Check rate limit."""
        if self.rate_limiter:
            return self.rate_limiter.is_allowed(self.__class__.__name__)
        return True, None


class OllamaClient(AIClient):
    """Ollama AI client for local models."""
    
    def ask(self, question: str, verbose: bool = False) -> str:
        """Ask Ollama a question."""
        # Check cache first
        cached = self._check_cache(question)
        if cached:
            return cached
        
        # Check rate limit
        allowed, error = self._check_rate_limit()
        if not allowed:
            raise Exception(error)
        
        base_url = self.config.base_url or "http://localhost:11434"
        model = self.config.model or "llama3.2"
        
        try:
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": question,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            answer = result.get("response", "No response from Ollama.")
            
            # Save to cache
            self._save_cache(question, answer)
            
            return answer
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to Ollama: {str(e)}")


class OpenAIClient(AIClient):
    """OpenAI API client."""
    
    def ask(self, question: str, verbose: bool = False) -> str:
        """Ask OpenAI a question."""
        # Check cache first
        cached = self._check_cache(question)
        if cached:
            return cached
        
        # Check rate limit
        allowed, error = self._check_rate_limit()
        if not allowed:
            raise Exception(error)
        
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        model = self.config.model or "gpt-4o-mini"
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.7,
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            # Save to cache
            self._save_cache(question, answer)
            
            return answer
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to OpenAI: {str(e)}")


class AnthropicClient(AIClient):
    """Anthropic (Claude) API client."""
    
    def ask(self, question: str, verbose: bool = False) -> str:
        """Ask Anthropic a question."""
        # Check cache first
        cached = self._check_cache(question)
        if cached:
            return cached
        
        # Check rate limit
        allowed, error = self._check_rate_limit()
        if not allowed:
            raise Exception(error)
        
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        model = self.config.model or "claude-3-5-sonnet-20241022"
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": question}
                    ],
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            answer = result["content"][0]["text"]
            
            # Save to cache
            self._save_cache(question, answer)
            
            return answer
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to Anthropic: {str(e)}")


class DeepSeekClient(AIClient):
    """DeepSeek API client."""
    
    def ask(self, question: str, verbose: bool = False) -> str:
        """Ask DeepSeek a question."""
        # Check cache first
        cached = self._check_cache(question)
        if cached:
            return cached
        
        # Check rate limit
        allowed, error = self._check_rate_limit()
        if not allowed:
            raise Exception(error)
        
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise Exception("DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable.")
        
        base_url = self.config.base_url or "https://api.deepseek.com"
        model = self.config.model or "deepseek-chat"
        
        try:
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.7,
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            # Save to cache
            self._save_cache(question, answer)
            
            return answer
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to DeepSeek: {str(e)}")


def create_client(provider: str, config: ProviderConfig, rate_limiter: Optional[RateLimiter] = None,
                  cache: Optional[Cache] = None) -> AIClient:
    """Factory function to create appropriate AI client."""
    providers = {
        "ollama": OllamaClient,
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "deepseek": DeepSeekClient,
    }
    
    client_class = providers.get(provider.lower())
    if not client_class:
        raise ValueError(f"Unknown provider: {provider}")
    
    return client_class(config, rate_limiter, cache)

