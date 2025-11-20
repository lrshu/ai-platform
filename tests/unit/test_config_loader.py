"""
Unit tests for the configuration loader.
"""

import pytest
import os
import json5
from unittest.mock import mock_open, patch
from app.common.config_loader import ConfigLoader


def test_config_loader_initialization():
    """Test ConfigLoader initialization."""
    # This test would require a config file to exist
    # For now, we'll skip it or mock the file reading
    pass


@patch("builtins.open", new_callable=mock_open, read_data='{"test": "value"}')
def test_config_loader_load_config(mock_file):
    """Test loading configuration from file."""
    loader = ConfigLoader("test_config.json5")
    assert loader.config == {"test": "value"}
    mock_file.assert_called_once_with("test_config.json5", 'r', encoding='utf-8')


def test_config_loader_get_value():
    """Test getting configuration values."""
    loader = ConfigLoader.__new__(ConfigLoader)
    loader.config = {
        "database": {
            "uri": "bolt://localhost:7687"
        },
        "nested": {
            "deeply": {
                "value": "test"
            }
        }
    }

    # Test existing value
    assert loader.get("database.uri") == "bolt://localhost:7687"

    # Test nested value
    assert loader.get("nested.deeply.value") == "test"

    # Test default value for non-existing key
    assert loader.get("non.existing.key", "default") == "default"

    # Test None for non-existing key without default
    assert loader.get("non.existing.key") is None


def test_config_loader_get_provider_class():
    """Test getting provider class paths."""
    loader = ConfigLoader.__new__(ConfigLoader)
    loader.config = {
        "provider_map": {
            "Qwen": "app.providers.qwen_provider.QwenProvider",
            "Mineru": "app.providers.mineru_provider.MineruProvider"
        }
    }

    assert loader.get_provider_class("Qwen") == "app.providers.qwen_provider.QwenProvider"
    assert loader.get_provider_class("Mineru") == "app.providers.mineru_provider.MineruProvider"
    assert loader.get_provider_class("NonExistent") == ""


def test_config_loader_get_capability_config():
    """Test getting capability configuration."""
    loader = ConfigLoader.__new__(ConfigLoader)
    loader.config = {
        "pipeline_capabilities": {
            "embedder": {
                "provider": "Qwen",
                "name": "text-embedding-v4"
            },
            "generator": {
                "provider": "Qwen",
                "name": "qwen-plus"
            }
        }
    }

    embedder_config = loader.get_capability_config("embedder")
    assert embedder_config == {"provider": "Qwen", "name": "text-embedding-v4"}

    generator_config = loader.get_capability_config("generator")
    assert generator_config == {"provider": "Qwen", "name": "qwen-plus"}

    empty_config = loader.get_capability_config("nonexistent")
    assert empty_config == {}