"""
Tests for the API endpoints.

This module tests the functionality of the FastAPI application,
including uploading papers and querying the system.
"""

import os
import json
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from papershelf.api.app import app, create_app


class TestAPI:
    """Test cases for the API endpoints."""

    def test_root_endpoint(self, api_client):
        """Test the root endpoint."""
        response = api_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to PaperShelf API"}

    @patch('papershelf.api.app.pdf_processor')
    @patch('papershelf.api.app.embedding_generator')
    @patch('papershelf.api.app.vector_store')
    def test_upload_endpoint(self, mock_vector_store, mock_embedding_generator, mock_pdf_processor, api_client, sample_pdf_path):
        """Test the upload endpoint."""
        # Set up mocks
        mock_pdf_processor.extract_metadata.return_value = {
            "title": "Test Paper",
            "author": "Test Author",
            "page_count": 10,
            "file_path": sample_pdf_path
        }
        mock_pdf_processor.process_pdf.return_value = ["Chunk 1", "Chunk 2"]
        mock_embedding_generator.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        # Test uploading a PDF
        with open(sample_pdf_path, "rb") as f:
            response = api_client.post(
                "/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Paper"
        assert data["author"] == "Test Author"
        assert data["page_count"] == 10
        assert data["status"] == "success"
        
        # Check that the mocks were called correctly
        mock_pdf_processor.extract_metadata.assert_called_once()
        mock_pdf_processor.process_pdf.assert_called_once()
        mock_embedding_generator.generate_embeddings.assert_called_once_with(["Chunk 1", "Chunk 2"])
        mock_vector_store.add_documents.assert_called_once()

    def test_upload_endpoint_invalid_file(self, api_client):
        """Test the upload endpoint with an invalid file type."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"This is not a PDF file")
            temp_file.flush()
            
            # Test uploading a non-PDF file
            with open(temp_file.name, "rb") as f:
                response = api_client.post(
                    "/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            # Check the response
            assert response.status_code == 400
            assert "File must be a PDF" in response.json()["detail"]

    @patch('papershelf.api.app.rag_engine')
    def test_query_endpoint(self, mock_rag_engine, api_client):
        """Test the query endpoint."""
        # Set up mock
        mock_rag_engine.query.return_value = {
            "query": "test query",
            "answer": "This is a test answer.",
            "retrieved_documents": [
                {"id": "doc1", "text": "Document 1", "metadata": {"source": "test1"}},
                {"id": "doc2", "text": "Document 2", "metadata": {"source": "test2"}}
            ]
        }
        
        # Test querying
        response = api_client.post(
            "/query",
            json={"query": "test query", "top_k": 2}
        )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test query"
        assert data["answer"] == "This is a test answer."
        assert len(data["retrieved_documents"]) == 2
        
        # Check that the mock was called correctly
        mock_rag_engine.query.assert_called_once_with("test query")

    @patch('papershelf.api.app.rag_engine')
    def test_query_endpoint_error(self, mock_rag_engine, api_client):
        """Test the query endpoint with an error."""
        # Set up mock to raise an exception
        mock_rag_engine.query.side_effect = Exception("Test error")
        
        # Test querying
        response = api_client.post(
            "/query",
            json={"query": "test query"}
        )
        
        # Check the response
        assert response.status_code == 500
        assert "Error querying papers" in response.json()["detail"]

    @patch('papershelf.api.app.vector_store')
    def test_stats_endpoint(self, mock_vector_store, api_client):
        """Test the stats endpoint."""
        # Set up mock
        mock_vector_store.get_collection_stats.return_value = {
            "count": 10,
            "collection_name": "academic_papers",
            "persist_directory": "./chroma_db"
        }
        
        # Test getting stats
        response = api_client.get("/stats")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert data["collection_name"] == "academic_papers"
        assert data["persist_directory"] == "./chroma_db"
        
        # Check that the mock was called correctly
        mock_vector_store.get_collection_stats.assert_called_once()

    @patch('papershelf.api.app.vector_store')
    def test_stats_endpoint_error(self, mock_vector_store, api_client):
        """Test the stats endpoint with an error."""
        # Set up mock to raise an exception
        mock_vector_store.get_collection_stats.side_effect = Exception("Test error")
        
        # Test getting stats
        response = api_client.get("/stats")
        
        # Check the response
        assert response.status_code == 500
        assert "Error getting stats" in response.json()["detail"]

    def test_create_app(self):
        """Test the create_app function."""
        # Test creating the app
        test_app = create_app()
        
        # Check that we got a FastAPI app
        assert test_app is not None
        assert test_app.title == "PaperShelf API"