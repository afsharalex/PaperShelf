"""
Tests for the embedding generator module.

This module tests the functionality of generating embeddings from text.
"""

import pytest
from unittest.mock import patch, MagicMock

import numpy as np

from papershelf.ingest.embedding_generator import EmbeddingGenerator


class TestEmbeddingGenerator:
    """Test cases for the EmbeddingGenerator class."""

    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Test with default parameters
        generator = EmbeddingGenerator()
        assert generator.model_name == "all-MiniLM-L6-v2"
        
        # Test with custom parameters
        generator = EmbeddingGenerator(model_name="paraphrase-MiniLM-L6-v2")
        assert generator.model_name == "paraphrase-MiniLM-L6-v2"

    def test_generate_embeddings_single_text(self, embedding_generator):
        """Test generating embeddings for a single text."""
        text = "This is a test sentence for embedding generation."
        
        # Generate embeddings
        embeddings = embedding_generator.generate_embeddings(text)
        
        # Check that we got a list of embeddings
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        
        # Check that the embedding is a list of floats
        assert isinstance(embeddings[0], list)
        assert all(isinstance(x, float) for x in embeddings[0])
        
        # Check that the embedding has the expected dimension
        # The all-MiniLM-L6-v2 model produces 384-dimensional embeddings
        assert len(embeddings[0]) == 384

    def test_generate_embeddings_multiple_texts(self, embedding_generator):
        """Test generating embeddings for multiple texts."""
        texts = [
            "This is the first test sentence.",
            "This is the second test sentence.",
            "This is the third test sentence."
        ]
        
        # Generate embeddings
        embeddings = embedding_generator.generate_embeddings(texts)
        
        # Check that we got a list of embeddings
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        
        # Check that each embedding is a list of floats
        for embedding in embeddings:
            assert isinstance(embedding, list)
            assert all(isinstance(x, float) for x in embedding)
            
            # Check that each embedding has the expected dimension
            assert len(embedding) == 384

    @patch('papershelf.ingest.embedding_generator.SentenceTransformer')
    def test_generate_embeddings_with_mock(self, mock_sentence_transformer):
        """Test generating embeddings using a mock SentenceTransformer."""
        # Set up the mock
        mock_model = MagicMock()
        mock_sentence_transformer.return_value = mock_model
        
        # Set up the mock to return a numpy array of embeddings
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.2, 0.3, 0.4, 0.5, 0.6]
        ])
        mock_model.encode.return_value = mock_embeddings
        
        # Create the generator with the mock
        generator = EmbeddingGenerator()
        
        # Test with multiple texts
        texts = ["Text 1", "Text 2"]
        embeddings = generator.generate_embeddings(texts)
        
        # Check that the mock was called correctly
        mock_model.encode.assert_called_once_with(texts, convert_to_tensor=False)
        
        # Check that we got the expected embeddings
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3, 0.4, 0.5]
        assert embeddings[1] == [0.2, 0.3, 0.4, 0.5, 0.6]

    def test_get_model_info(self, embedding_generator):
        """Test getting model information."""
        # Get model info
        info = embedding_generator.get_model_info()
        
        # Check that we got a dictionary with the expected keys
        assert isinstance(info, dict)
        assert "model_name" in info
        assert "model_dimension" in info
        assert "model_max_seq_length" in info
        
        # Check specific values
        assert info["model_name"] == "all-MiniLM-L6-v2"
        assert info["model_dimension"] == "384"  # This is the dimension for all-MiniLM-L6-v2