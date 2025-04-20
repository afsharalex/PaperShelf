"""
Tests for the configuration module.

This module tests the functionality of loading environment variables and
configuration settings.
"""

import os
from unittest.mock import patch

import pytest

from papershelf.utils.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        # Check default values
        assert Config.API_HOST == "0.0.0.0"
        assert Config.API_PORT == 8000
        assert Config.DB_PERSIST_DIRECTORY == "./chroma_db"
        assert Config.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
        assert Config.LLM_MODEL == "gpt-3.5-turbo"
        assert Config.LLM_TEMPERATURE == 0.0
        assert Config.LLM_MAX_TOKENS == 500
        assert Config.CHUNK_SIZE == 1000
        assert Config.CHUNK_OVERLAP == 200

    @patch.dict(os.environ, {
        "API_HOST": "127.0.0.1",
        "API_PORT": "9000",
        "DB_PERSIST_DIRECTORY": "./custom_db",
        "EMBEDDING_MODEL": "custom-model",
        "LLM_MODEL": "gpt-4",
        "LLM_TEMPERATURE": "0.5",
        "LLM_MAX_TOKENS": "1000",
        "CHUNK_SIZE": "500",
        "CHUNK_OVERLAP": "100",
        "OPENAI_API_KEY": "test-key"
    })
    def test_environment_variables(self):
        """Test that environment variables are loaded correctly."""
        # Reload the config module to pick up the environment variables
        from importlib import reload
        from papershelf.utils import config
        reload(config)
        
        # Check that environment variables were loaded
        assert config.Config.API_HOST == "127.0.0.1"
        assert config.Config.API_PORT == 9000
        assert config.Config.DB_PERSIST_DIRECTORY == "./custom_db"
        assert config.Config.EMBEDDING_MODEL == "custom-model"
        assert config.Config.LLM_MODEL == "gpt-4"
        assert config.Config.LLM_TEMPERATURE == 0.5
        assert config.Config.LLM_MAX_TOKENS == 1000
        assert config.Config.CHUNK_SIZE == 500
        assert config.Config.CHUNK_OVERLAP == 100
        assert config.Config.OPENAI_API_KEY == "test-key"
        
        # Reset the config module
        reload(config)

    def test_get_all(self):
        """Test the get_all method."""
        # Get all config settings
        config_dict = Config.get_all()
        
        # Check that we got a dictionary with the expected structure
        assert isinstance(config_dict, dict)
        assert "api" in config_dict
        assert "database" in config_dict
        assert "embedding" in config_dict
        assert "llm" in config_dict
        assert "pdf_processing" in config_dict
        
        # Check specific values
        assert config_dict["api"]["host"] == Config.API_HOST
        assert config_dict["api"]["port"] == Config.API_PORT
        assert config_dict["database"]["persist_directory"] == Config.DB_PERSIST_DIRECTORY
        assert config_dict["embedding"]["model"] == Config.EMBEDDING_MODEL
        assert config_dict["llm"]["model"] == Config.LLM_MODEL
        assert config_dict["llm"]["temperature"] == Config.LLM_TEMPERATURE
        assert config_dict["llm"]["max_tokens"] == Config.LLM_MAX_TOKENS
        assert config_dict["pdf_processing"]["chunk_size"] == Config.CHUNK_SIZE
        assert config_dict["pdf_processing"]["chunk_overlap"] == Config.CHUNK_OVERLAP