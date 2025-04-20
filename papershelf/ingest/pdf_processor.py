"""
PDF processing module for PaperShelf.

This module provides functionality to extract text from PDF files
and prepare it for embedding generation.
"""

import os
from typing import Dict, List, Optional

from pypdf import PdfReader


class PDFProcessor:
    """Class for processing PDF files and extracting text."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the PDF processor.

        Args:
            chunk_size: The size of text chunks for processing
            chunk_overlap: The overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        reader = PdfReader(pdf_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        return text

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing.

        Args:
            text: The text to chunk

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
            
        return chunks

    def process_pdf(self, pdf_path: str) -> List[str]:
        """
        Process a PDF file and return chunked text.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of text chunks from the PDF
        """
        text = self.extract_text(pdf_path)
        chunks = self.chunk_text(text)
        return chunks

    def extract_metadata(self, pdf_path: str) -> Dict[str, str]:
        """
        Extract metadata from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary of metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        
        result = {
            "title": metadata.get("/Title", os.path.basename(pdf_path)),
            "author": metadata.get("/Author", "Unknown"),
            "subject": metadata.get("/Subject", ""),
            "keywords": metadata.get("/Keywords", ""),
            "creator": metadata.get("/Creator", ""),
            "producer": metadata.get("/Producer", ""),
            "file_path": pdf_path,
            "page_count": len(reader.pages)
        }
        
        return result