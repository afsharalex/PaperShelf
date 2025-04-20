"""
Embedding generator module for PaperShelf.

This module provides functionality to generate embeddings from text
using sentence transformers.
"""

from typing import Dict, List, Optional, Union

from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """Class for generating embeddings from text."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings for the given texts.

        Args:
            texts: A single text string or a list of text strings

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if isinstance(texts, str):
            texts = [texts]
            
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        
        return embeddings.tolist()

    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the embedding model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "model_dimension": str(self.model.get_sentence_embedding_dimension()),
            "model_max_seq_length": str(self.model.get_max_seq_length())
        }