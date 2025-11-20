"""
Configuration loader for the RAG backend system.
Supports JSON5 format with comments and environment variable overrides.
"""

import os
from typing import Any, Dict
import json5


class ConfigLoader:
    """Load and manage application configuration."""

    def __init__(self, config_file: str = "config.json5"):
        """
        Initialize the configuration loader.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file and apply environment variable overrides.

        Returns:
            Configuration dictionary
        """
        # Load base configuration from file
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json5.load(f)

        # Apply environment variable overrides
        self._apply_env_overrides(config)

        return config

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """
        Apply environment variable overrides to configuration.

        Args:
            config: Configuration dictionary to modify
        """
        # Database configuration overrides
        if 'database' in config:
            if 'uri' in config['database']:
                config['database']['uri'] = os.getenv('MEMGRAPH_URI', config['database']['uri'])
            if 'user' in config['database']:
                config['database']['user'] = os.getenv('MEMGRAPH_USER', config['database']['user'])
            if 'password' in config['database']:
                config['database']['password'] = os.getenv('MEMGRAPH_PASSWORD', config['database']['password'])

        # DashScope API key override
        if 'DASHSCOPE_API_KEY' in os.environ:
            config['dashscope_api_key'] = os.environ['DASHSCOPE_API_KEY']

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the configuration value (e.g., "database.uri")
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_provider_class(self, provider_name: str) -> str:
        """
        Get the class path for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Class path string
        """
        return self.config.get('provider_map', {}).get(provider_name, '')

    def get_capability_config(self, capability: str) -> Dict[str, Any]:
        """
        Get configuration for a specific capability.

        Args:
            capability: Name of the capability (embedder, generator, etc.)

        Returns:
            Capability configuration dictionary
        """
        return self.config.get('pipeline_capabilities', {}).get(capability, {})


# Global configuration instance
config_loader = ConfigLoader()