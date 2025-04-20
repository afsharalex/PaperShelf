"""
Tests for the RAG engine module.

This module tests the functionality of querying the vector database and generating
responses using LangGraph.
"""

import pytest
from unittest.mock import patch, MagicMock

from papershelf.query.rag_engine import RAGEngine
from papershelf.db.vector_store import VectorStore
from papershelf.ingest.embedding_generator import EmbeddingGenerator


class TestRAGEngine:
    """Test cases for the RAGEngine class."""

    def test_init(self, vector_store, embedding_generator):
        """Test initialization with default and custom parameters."""
        # Test with provided components
        engine = RAGEngine(
            vector_store=vector_store,
            embedding_generator=embedding_generator
        )
        assert engine.vector_store is vector_store
        assert engine.embedding_generator is embedding_generator
        assert engine.model_name == "gpt-3.5-turbo"
        assert engine.temperature == 0.0
        assert engine.max_tokens == 500
        assert engine.top_k == 5
        
        # Test with custom parameters
        engine = RAGEngine(
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_k=10
        )
        assert engine.model_name == "gpt-4"
        assert engine.temperature == 0.7
        assert engine.max_tokens == 1000
        assert engine.top_k == 10

    def test_build_graph(self, vector_store, embedding_generator):
        """Test building the LangGraph for RAG."""
        engine = RAGEngine(
            vector_store=vector_store,
            embedding_generator=embedding_generator
        )
        
        # Check that the graph was built
        assert engine.graph is not None

    @patch('papershelf.query.rag_engine.ChatOpenAI')
    def test_query_with_mocks(self, mock_chat_openai, vector_store, embedding_generator):
        """Test querying the RAG engine with mocked components."""
        # Set up mocks
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.invoke.return_value.content = "This is a mock answer."
        
        # Mock the embedding generator
        embedding_generator.generate_embeddings = MagicMock(return_value=[[0.1, 0.2, 0.3, 0.4, 0.5]])
        
        # Mock the vector store
        vector_store.query = MagicMock(return_value={
            "ids": [["doc1", "doc2"]],
            "documents": [["Document 1 content", "Document 2 content"]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]]
        })
        
        # Create the engine with mocked components
        engine = RAGEngine(
            vector_store=vector_store,
            embedding_generator=embedding_generator
        )
        
        # Replace the graph with a simpler mock
        engine.graph = MagicMock()
        engine.graph.invoke.return_value = {
            "query": "test query",
            "retrieved_documents": [
                {"id": "doc1", "text": "Document 1 content", "metadata": {"source": "test1"}},
                {"id": "doc2", "text": "Document 2 content", "metadata": {"source": "test2"}}
            ],
            "answer": "This is a mock answer."
        }
        
        # Test the query method
        result = engine.query("test query")
        
        # Check that the graph was invoked
        engine.graph.invoke.assert_called_once_with({"query": "test query"})
        
        # Check the result structure
        assert "query" in result
        assert "answer" in result
        assert "retrieved_documents" in result
        assert result["query"] == "test query"
        assert result["answer"] == "This is a mock answer."
        assert len(result["retrieved_documents"]) == 2

    @patch('papershelf.query.rag_engine.StateGraph')
    def test_graph_nodes(self, mock_state_graph, vector_store, embedding_generator):
        """Test that the graph has the expected nodes."""
        # Set up mocks
        mock_graph = MagicMock()
        mock_state_graph.return_value = mock_graph
        mock_graph.compile.return_value = mock_graph
        
        # Create the engine
        engine = RAGEngine(
            vector_store=vector_store,
            embedding_generator=embedding_generator
        )
        
        # Check that the graph was built with the expected nodes
        mock_graph.add_node.assert_any_call("retrieve_documents", pytest.ANY)
        mock_graph.add_node.assert_any_call("generate_answer", pytest.ANY)
        
        # Check that the edges were added
        mock_graph.add_edge.assert_any_call("retrieve_documents", "generate_answer")
        mock_graph.add_edge.assert_any_call("generate_answer", "END")
        
        # Check that the entry point was set
        mock_graph.set_entry_point.assert_called_once_with("retrieve_documents")