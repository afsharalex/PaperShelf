"""
Pytest configuration file for PaperShelf tests.

This file contains fixtures that can be used across all test files.
"""

import os
import tempfile
from typing import Dict, Generator, List

import pytest
from fastapi.testclient import TestClient

from papershelf.api.app import create_app
from papershelf.db.vector_store import VectorStore
from papershelf.ingest.embedding_generator import EmbeddingGenerator
from papershelf.ingest.pdf_processor import PDFProcessor
from papershelf.query.rag_engine import RAGEngine


@pytest.fixture
def sample_text() -> str:
    """Fixture that returns a sample text for testing."""
    return """
    This is a sample academic paper text.
    It contains multiple sentences that can be used for testing.
    The paper discusses various aspects of machine learning and natural language processing.
    Embeddings are vector representations of text that capture semantic meaning.
    """


@pytest.fixture
def sample_pdf_path() -> Generator[str, None, None]:
    """
    Fixture that creates a temporary PDF file for testing.
    
    This is a simple text-based PDF for testing purposes.
    For more complex PDF testing, consider using a real academic paper PDF.
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple PDF file with some text
        pdf_path = os.path.join(temp_dir, "sample.pdf")
        
        # Use a simple command to create a basic PDF
        # This is a placeholder - in a real implementation, you might want to use
        # a library like reportlab to create a more realistic PDF
        with open(pdf_path, "w") as f:
            f.write("%PDF-1.7\n")
            f.write("1 0 obj\n")
            f.write("<< /Type /Catalog /Pages 2 0 R >>\n")
            f.write("endobj\n")
            f.write("2 0 obj\n")
            f.write("<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n")
            f.write("endobj\n")
            f.write("3 0 obj\n")
            f.write("<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\n")
            f.write("endobj\n")
            f.write("4 0 obj\n")
            f.write("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n")
            f.write("endobj\n")
            f.write("5 0 obj\n")
            f.write("<< /Length 68 >>\n")
            f.write("stream\n")
            f.write("BT\n")
            f.write("/F1 12 Tf\n")
            f.write("100 700 Td\n")
            f.write("(This is a sample academic paper for testing.) Tj\n")
            f.write("ET\n")
            f.write("endstream\n")
            f.write("endobj\n")
            f.write("xref\n")
            f.write("0 6\n")
            f.write("0000000000 65535 f\n")
            f.write("0000000010 00000 n\n")
            f.write("0000000060 00000 n\n")
            f.write("0000000120 00000 n\n")
            f.write("0000000220 00000 n\n")
            f.write("0000000290 00000 n\n")
            f.write("trailer\n")
            f.write("<< /Size 6 /Root 1 0 R >>\n")
            f.write("startxref\n")
            f.write("410\n")
            f.write("%%EOF\n")
        
        yield pdf_path


@pytest.fixture
def pdf_processor() -> PDFProcessor:
    """Fixture that returns a PDFProcessor instance for testing."""
    return PDFProcessor(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def embedding_generator() -> EmbeddingGenerator:
    """
    Fixture that returns an EmbeddingGenerator instance for testing.
    
    Note: This uses a real model which might slow down tests.
    Consider mocking this for faster tests.
    """
    return EmbeddingGenerator(model_name="all-MiniLM-L6-v2")


@pytest.fixture
def vector_store() -> Generator[VectorStore, None, None]:
    """
    Fixture that returns a VectorStore instance for testing.
    
    Uses a temporary directory for the database that is cleaned up after tests.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(persist_directory=temp_dir)
        yield store


@pytest.fixture
def rag_engine(vector_store: VectorStore, embedding_generator: EmbeddingGenerator) -> RAGEngine:
    """
    Fixture that returns a RAGEngine instance for testing.
    
    Note: This requires an OpenAI API key to be set in the environment.
    For testing without an API key, consider mocking the LLM responses.
    """
    return RAGEngine(
        vector_store=vector_store,
        embedding_generator=embedding_generator,
        model_name="gpt-3.5-turbo",
        temperature=0.0,
        max_tokens=100
    )


@pytest.fixture
def api_client() -> TestClient:
    """Fixture that returns a TestClient for testing the API."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_embeddings() -> List[List[float]]:
    """Fixture that returns sample embeddings for testing."""
    # These are just example embeddings (dimensionality reduced for brevity)
    return [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.2, 0.3, 0.4, 0.5, 0.6],
        [0.3, 0.4, 0.5, 0.6, 0.7]
    ]


@pytest.fixture
def sample_metadata() -> Dict[str, str]:
    """Fixture that returns sample metadata for testing."""
    return {
        "title": "Sample Academic Paper",
        "author": "Test Author",
        "subject": "Machine Learning",
        "keywords": "ML, AI, NLP",
        "page_count": "10"
    }