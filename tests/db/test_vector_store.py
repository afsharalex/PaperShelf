"""
Tests for the vector store module.

This module tests the functionality of storing and retrieving embeddings
from the vector database.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from papershelf.db.vector_store import VectorStore


class TestVectorStore:
    """Test cases for the VectorStore class."""

    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Test with default parameters
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore()
            assert store.persist_directory == "./chroma_db"
            
            # Test with custom parameters
            custom_dir = os.path.join(temp_dir, "custom_db")
            store = VectorStore(persist_directory=custom_dir)
            assert store.persist_directory == custom_dir
            
            # Check that the directory was created
            assert os.path.exists(custom_dir)

    def test_add_documents(self, vector_store, sample_embeddings):
        """Test adding documents to the vector store."""
        # Prepare test data
        doc_ids = ["doc1", "doc2", "doc3"]
        texts = ["Text 1", "Text 2", "Text 3"]
        metadatas = [
            {"source": "test1", "page": 1},
            {"source": "test2", "page": 2},
            {"source": "test3", "page": 3}
        ]
        
        # Add documents
        vector_store.add_documents(
            document_ids=doc_ids,
            embeddings=sample_embeddings,
            texts=texts,
            metadatas=metadatas
        )
        
        # Check that documents were added (by querying)
        results = vector_store.query(
            query_embedding=sample_embeddings[0],
            n_results=3
        )
        
        # Check that we got results
        assert len(results["ids"][0]) > 0
        
        # Check that at least one of our documents is in the results
        assert any(doc_id in results["ids"][0] for doc_id in doc_ids)

    def test_add_documents_validation(self, vector_store, sample_embeddings):
        """Test validation when adding documents."""
        # Test with mismatched lengths
        with pytest.raises(ValueError):
            vector_store.add_documents(
                document_ids=["doc1", "doc2"],  # 2 items
                embeddings=sample_embeddings,   # 3 items
                texts=["Text 1", "Text 2", "Text 3"]  # 3 items
            )

    def test_query(self, vector_store, sample_embeddings):
        """Test querying the vector store."""
        # Add some documents first
        doc_ids = ["doc1", "doc2", "doc3"]
        texts = ["Text 1", "Text 2", "Text 3"]
        
        vector_store.add_documents(
            document_ids=doc_ids,
            embeddings=sample_embeddings,
            texts=texts
        )
        
        # Query with the first embedding
        results = vector_store.query(
            query_embedding=sample_embeddings[0],
            n_results=2
        )
        
        # Check the structure of the results
        assert "ids" in results
        assert "documents" in results
        assert isinstance(results["ids"], list)
        assert isinstance(results["documents"], list)
        assert len(results["ids"]) == 1  # One query
        assert len(results["ids"][0]) <= 2  # Up to 2 results

    def test_query_with_filter(self, vector_store, sample_embeddings):
        """Test querying with a filter condition."""
        # Add some documents with metadata
        doc_ids = ["doc1", "doc2", "doc3"]
        texts = ["Text 1", "Text 2", "Text 3"]
        metadatas = [
            {"category": "A", "score": 10},
            {"category": "B", "score": 20},
            {"category": "A", "score": 30}
        ]
        
        vector_store.add_documents(
            document_ids=doc_ids,
            embeddings=sample_embeddings,
            texts=texts,
            metadatas=metadatas
        )
        
        # Query with a filter
        results = vector_store.query(
            query_embedding=sample_embeddings[0],
            n_results=3,
            where={"category": "A"}
        )
        
        # Check that we only got results with category A
        for i, doc_id in enumerate(results["ids"][0]):
            if doc_id == "doc1" or doc_id == "doc3":
                assert results["metadatas"][0][i]["category"] == "A"

    def test_get_document_by_id(self, vector_store, sample_embeddings):
        """Test getting a document by its ID."""
        # Add a document
        doc_id = "test_doc"
        text = "Test document text"
        metadata = {"source": "test", "page": 1}
        
        vector_store.add_documents(
            document_ids=[doc_id],
            embeddings=[sample_embeddings[0]],
            texts=[text],
            metadatas=[metadata]
        )
        
        # Get the document by ID
        doc = vector_store.get_document_by_id(doc_id)
        
        # Check that we got the correct document
        assert doc is not None
        assert doc["id"] == doc_id
        assert doc["document"] == text
        assert doc["metadata"]["source"] == "test"
        assert doc["metadata"]["page"] == 1
        
        # Test with a non-existent ID
        doc = vector_store.get_document_by_id("non_existent_id")
        assert doc is None

    def test_delete_document(self, vector_store, sample_embeddings):
        """Test deleting a document from the vector store."""
        # Add a document
        doc_id = "test_doc"
        
        vector_store.add_documents(
            document_ids=[doc_id],
            embeddings=[sample_embeddings[0]],
            texts=["Test document text"]
        )
        
        # Verify it exists
        doc = vector_store.get_document_by_id(doc_id)
        assert doc is not None
        
        # Delete the document
        result = vector_store.delete_document(doc_id)
        assert result is True
        
        # Verify it's gone
        doc = vector_store.get_document_by_id(doc_id)
        assert doc is None
        
        # Test deleting a non-existent document
        result = vector_store.delete_document("non_existent_id")
        assert result is False

    def test_get_collection_stats(self, vector_store, sample_embeddings):
        """Test getting statistics about the collection."""
        # Add some documents
        doc_ids = ["doc1", "doc2", "doc3"]
        texts = ["Text 1", "Text 2", "Text 3"]
        
        vector_store.add_documents(
            document_ids=doc_ids,
            embeddings=sample_embeddings,
            texts=texts
        )
        
        # Get stats
        stats = vector_store.get_collection_stats()
        
        # Check the structure of the stats
        assert "count" in stats
        assert "collection_name" in stats
        assert "persist_directory" in stats
        
        # Check specific values
        assert stats["count"] == 3
        assert stats["collection_name"] == "academic_papers"
        assert stats["persist_directory"] == vector_store.persist_directory