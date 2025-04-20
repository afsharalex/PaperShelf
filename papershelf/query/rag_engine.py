"""
RAG engine module for PaperShelf.

This module provides functionality to query the vector database and generate
responses using LangGraph for RAG functionality.
"""

import os
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langgraph.graph import END, StateGraph

from papershelf.db.vector_store import VectorStore
from papershelf.ingest.embedding_generator import EmbeddingGenerator


class RAGEngine:
    """Class for RAG-based querying of academic papers."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        max_tokens: int = 500,
        top_k: int = 5
    ):
        """
        Initialize the RAG engine.

        Args:
            vector_store: Vector store instance
            embedding_generator: Embedding generator instance
            model_name: Name of the LLM model to use
            temperature: Temperature for the LLM
            max_tokens: Maximum tokens for the LLM response
            top_k: Number of documents to retrieve
        """
        self.vector_store = vector_store or VectorStore()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_k = top_k

        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Initialize the RAG graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph for RAG.

        Returns:
            StateGraph instance
        """
        # Define the state schema
        @dataclass
        class GraphState:
            query: str
            retrieved_documents: Optional[List[Dict]] = None
            answer: Optional[str] = None

        # Create the graph
        graph = StateGraph(GraphState)

        # Define the nodes
        def retrieve_documents(state: GraphState) -> Dict[str, Any]:
            """Retrieve relevant documents from the vector store."""
            query = state.query

            # Generate embedding for the query
            query_embedding = self.embedding_generator.generate_embeddings(query)[0]

            # Query the vector store
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=self.top_k
            )

            # Format the retrieved documents
            retrieved_documents = []
            for i in range(len(results["ids"][0])):
                retrieved_documents.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })

            return {"retrieved_documents": retrieved_documents}

        def generate_answer(state: GraphState) -> Dict[str, Any]:
            """Generate an answer based on the retrieved documents."""
            query = state.query
            retrieved_documents = state.retrieved_documents

            # Prepare context from retrieved documents
            context = "\n\n".join([f"Document {i+1}:\n{doc['text']}" for i, doc in enumerate(retrieved_documents)])

            # Generate prompt
            prompt = f"""
            You are an academic assistant helping with research papers.
            Answer the following question based on the provided context from academic papers.
            If the answer cannot be derived from the context, say "I don't have enough information to answer this question."

            Context:
            {context}

            Question: {query}

            Answer:
            """

            # Generate answer
            answer = self.llm.invoke(prompt).content

            return {"answer": answer}

        # Add nodes to the graph
        graph.add_node("retrieve_documents", retrieve_documents)
        graph.add_node("generate_answer", generate_answer)

        # Add edges
        graph.add_edge("retrieve_documents", "generate_answer")
        graph.add_edge("generate_answer", END)

        # Set the entry point
        graph.set_entry_point("retrieve_documents")

        return graph.compile()

    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Query the RAG engine.

        Args:
            query_text: The query text

        Returns:
            Dictionary with query results
        """
        # Run the graph
        result = self.graph.invoke({"query": query_text})

        return {
            "query": query_text,
            "answer": result["answer"],
            "retrieved_documents": result["retrieved_documents"]
        }
