"""
Unit tests for the PDF parser service.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from src.services.pdf_parser import PDFParser
from src.lib.exceptions import FileProcessingError


class TestPDFParser:
    """Test the PDF parser service."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.parser = PDFParser()

    def test_parse_pdf_success(self):
        """Test successful PDF parsing."""
        # Create a temporary PDF-like text file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("This is a test PDF content")
            temp_path = f.name

        # Mock the PdfReader to return our test content
        with patch('src.services.pdf_parser.PdfReader') as mock_reader:
            # Create a mock page object
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "This is a test PDF content"

            # Set up the mock reader
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance

            result = self.parser.parse_pdf(temp_path)
            assert result == "This is a test PDF content"

        # Clean up
        os.unlink(temp_path)

    def test_parse_pdf_file_not_found(self):
        """Test PDF parsing with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_pdf("/path/that/does/not/exist.pdf")

    def test_parse_pdf_invalid_extension(self):
        """Test PDF parsing with invalid file extension."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a text file")
            temp_path = f.name

        with pytest.raises(FileProcessingError):
            self.parser.parse_pdf(temp_path)

        # Clean up
        os.unlink(temp_path)

    def test_parse_pdf_reader_error(self):
        """Test PDF parsing when PdfReader fails."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("Invalid PDF content")
            temp_path = f.name

        with patch('src.services.pdf_parser.PdfReader') as mock_reader:
            mock_reader.side_effect = Exception("Failed to read PDF")

            with pytest.raises(FileProcessingError):
                self.parser.parse_pdf(temp_path)

        # Clean up
        os.unlink(temp_path)

    def test_get_pdf_metadata_success(self):
        """Test successful metadata extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("PDF content")
            temp_path = f.name

        # Mock metadata
        mock_metadata = {
            '/Title': 'Test Document',
            '/Author': 'Test Author',
            '/Subject': 'Test Subject'
        }

        with patch('src.services.pdf_parser.PdfReader') as mock_reader:
            mock_reader.return_value.metadata = mock_metadata

            result = self.parser.get_pdf_metadata(temp_path)
            assert result['Title'] == 'Test Document'
            assert result['Author'] == 'Test Author'
            assert result['Subject'] == 'Test Subject'

        # Clean up
        os.unlink(temp_path)

    def test_get_pdf_metadata_no_metadata(self):
        """Test metadata extraction when no metadata exists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("PDF content")
            temp_path = f.name

        with patch('src.services.pdf_parser.PdfReader') as mock_reader:
            mock_reader.return_value.metadata = None

            result = self.parser.get_pdf_metadata(temp_path)
            assert result == {}

        # Clean up
        os.unlink(temp_path)

    def test_get_page_count_success(self):
        """Test successful page count extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("PDF content")
            temp_path = f.name

        with patch('src.services.pdf_parser.PdfReader') as mock_reader:
            mock_reader.return_value.pages.__len__.return_value = 5

            result = self.parser.get_page_count(temp_path)
            assert result == 5

        # Clean up
        os.unlink(temp_path)

    def test_get_page_count_file_not_found(self):
        """Test page count extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.get_page_count("/path/that/does/not/exist.pdf")


if __name__ == "__main__":
    pytest.main([__file__])