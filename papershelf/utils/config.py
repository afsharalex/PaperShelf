"""
Configuration module for PaperShelf.

This module handles loading environment variables and configuration settings
for the PaperShelf application.
"""

import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for PaperShelf."""
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Database settings
    DB_PERSIST_DIRECTORY = os.getenv("DB_PERSIST_DIRECTORY", "./chroma_db")
    
    # Embedding settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # LLM settings
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
    
    # PDF processing settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # OpenAI API settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """
        Get all configuration settings as a dictionary.
        
        Returns:
            Dictionary of all configuration settings
        """
        return {
            "api": {
                "host": cls.API_HOST,
                "port": cls.API_PORT
            },
            "database": {
                "persist_directory": cls.DB_PERSIST_DIRECTORY
            },
            "embedding": {
                "model": cls.EMBEDDING_MODEL
            },
            "llm": {
                "model": cls.LLM_MODEL,
                "temperature": cls.LLM_TEMPERATURE,
                "max_tokens": cls.LLM_MAX_TOKENS
            },
            "pdf_processing": {
                "chunk_size": cls.CHUNK_SIZE,
                "chunk_overlap": cls.CHUNK_OVERLAP
            }
        }


# Create a singleton instance
config = Config()