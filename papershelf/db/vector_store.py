"""
Vector database module for PaperShelf.

This module provides functionality to store and retrieve embeddings
using ChromaDB as the vector database.
"""

import os
from typing import Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings


class VectorStore:
    """Class for managing the vector database."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        
        # Create the directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get the collection for papers
        self.collection = self.client.get_or_create_collection(
            name="academic_papers",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        document_ids: List[str],
        embeddings: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            document_ids: List of document IDs
            embeddings: List of embeddings
            texts: List of text chunks
            metadatas: List of metadata dictionaries
        """
        if len(document_ids) != len(embeddings) or len(document_ids) != len(texts):
            raise ValueError("document_ids, embeddings, and texts must have the same length")
            
        if metadatas is None:
            metadatas = [{} for _ in document_ids]
            
        self.collection.add(
            ids=document_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store for similar documents.

        Args:
            query_embedding: Embedding of the query
            n_results: Number of results to return
            where: Filter condition

        Returns:
            Dictionary with query results
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results

    def get_document_by_id(self, document_id: str) -> Optional[Dict]:
        """
        Get a document by its ID.

        Args:
            document_id: ID of the document

        Returns:
            Document data or None if not found
        """
        try:
            result = self.collection.get(ids=[document_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else {}
                }
            return None
        except Exception:
            return None

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            return True
        except Exception:
            return False

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "count": count,
            "collection_name": self.collection.name,
            "persist_directory": self.persist_directory
        }