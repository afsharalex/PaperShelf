"""
Tests for the PDF processor module.

This module tests the functionality of extracting text from PDFs and chunking it.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from papershelf.ingest.pdf_processor import PDFProcessor


class TestPDFProcessor:
    """Test cases for the PDFProcessor class."""

    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Test with default parameters
        processor = PDFProcessor()
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200

        # Test with custom parameters
        processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100

    def test_extract_text_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        processor = PDFProcessor()
        with pytest.raises(FileNotFoundError):
            processor.extract_text("non_existent_file.pdf")

    def test_extract_text(self, sample_pdf_path):
        """Test extracting text from a PDF file."""
        processor = PDFProcessor()
        
        # This test might need adjustment based on how your PDF extraction works
        # The sample_pdf_path fixture provides a very basic PDF
        text = processor.extract_text(sample_pdf_path)
        
        # Check that some text was extracted
        assert isinstance(text, str)
        assert len(text) > 0

    def test_chunk_text(self):
        """Test chunking text into smaller pieces."""
        processor = PDFProcessor(chunk_size=10, chunk_overlap=3)
        
        # Test with text shorter than chunk size
        text = "Short text"
        chunks = processor.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text
        
        # Test with text longer than chunk size
        text = "This is a longer text that should be split into multiple chunks"
        chunks = processor.chunk_text(text)
        
        # Check that we have multiple chunks
        assert len(chunks) > 1
        
        # Check that the chunks have the expected size
        for chunk in chunks[:-1]:  # All but the last chunk
            assert len(chunk) <= processor.chunk_size
        
        # Check that the chunks overlap correctly
        for i in range(len(chunks) - 1):
            overlap = chunks[i][-processor.chunk_overlap:]
            assert chunks[i+1].startswith(overlap)
        
        # Check that all text is included
        combined = chunks[0]
        for chunk in chunks[1:]:
            combined += chunk[processor.chunk_overlap:]
        assert combined == text

    def test_process_pdf(self, sample_pdf_path):
        """Test the full PDF processing pipeline."""
        processor = PDFProcessor(chunk_size=50, chunk_overlap=10)
        
        # Process the PDF
        chunks = processor.process_pdf(sample_pdf_path)
        
        # Check that we got some chunks
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        
        # Check that each chunk is a string
        for chunk in chunks:
            assert isinstance(chunk, str)

    def test_extract_metadata(self, sample_pdf_path):
        """Test extracting metadata from a PDF file."""
        processor = PDFProcessor()
        
        # Extract metadata
        metadata = processor.extract_metadata(sample_pdf_path)
        
        # Check that we got a dictionary with the expected keys
        assert isinstance(metadata, dict)
        assert "title" in metadata
        assert "author" in metadata
        assert "page_count" in metadata
        assert "file_path" in metadata
        
        # Check specific values
        assert metadata["file_path"] == sample_pdf_path
        assert metadata["page_count"] > 0

    @patch('papershelf.ingest.pdf_processor.PdfReader')
    def test_extract_metadata_with_mock(self, mock_pdf_reader, sample_pdf_path):
        """Test extracting metadata using a mock PdfReader."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_pdf_reader.return_value = mock_instance
        
        # Set up metadata
        mock_instance.metadata = {
            "/Title": "Test Title",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Keywords": "test, keywords",
            "/Creator": "Test Creator",
            "/Producer": "Test Producer"
        }
        mock_instance.pages = [MagicMock(), MagicMock()]  # Two pages
        
        # Test
        processor = PDFProcessor()
        metadata = processor.extract_metadata(sample_pdf_path)
        
        # Check results
        assert metadata["title"] == "Test Title"
        assert metadata["author"] == "Test Author"
        assert metadata["subject"] == "Test Subject"
        assert metadata["keywords"] == "test, keywords"
        assert metadata["creator"] == "Test Creator"
        assert metadata["producer"] == "Test Producer"
        assert metadata["page_count"] == 2