"""Integration tests for PDF parsing functionality."""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lib.pdf_parser import parse_pdf_to_markdown, extract_images_from_pdf


def test_parse_pdf_to_markdown_success():
    """Test successful PDF parsing to markdown."""
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Mock the fitz.open and page operations
        with patch('src.lib.pdf_parser.fitz.open') as mock_open:
            # Mock document
            mock_doc = MagicMock()
            mock_open.return_value = mock_doc

            # Mock pages
            mock_page1 = MagicMock()
            mock_page2 = MagicMock()
            mock_doc.__len__.return_value = 2
            mock_doc.load_page.side_effect = [mock_page1, mock_page2]

            # Mock page text extraction
            mock_page1.get_text.return_value = "This is page 1 content."
            mock_page2.get_text.return_value = "This is page 2 content."

            # Mock document close
            mock_doc.close.return_value = None

            # Call the function
            result = parse_pdf_to_markdown(tmp_path)

            # Verify the result
            expected = "## Page 1\n\nThis is page 1 content.\n\n## Page 2\n\nThis is page 2 content."
            assert result == expected

            # Verify the mock was called correctly
            mock_open.assert_called_once_with(tmp_path)
            mock_doc.load_page.assert_any_call(0)
            mock_doc.load_page.assert_any_call(1)
            mock_page1.get_text.assert_called_once()
            mock_page2.get_text.assert_called_once()
            mock_doc.close.assert_called_once()

    finally:
        # Clean up temporary file
        os.unlink(tmp_path)


def test_parse_pdf_to_markdown_file_not_found():
    """Test PDF parsing with file not found."""
    with pytest.raises(FileNotFoundError):
        parse_pdf_to_markdown("/path/to/nonexistent.pdf")


def test_parse_pdf_to_markdown_general_error():
    """Test PDF parsing with general error."""
    with patch('src.lib.pdf_parser.fitz.open') as mock_open:
        mock_open.side_effect = Exception("PDF parsing error")

        with pytest.raises(Exception) as exc_info:
            parse_pdf_to_markdown("/path/to/test.pdf")

        assert "Error parsing PDF file" in str(exc_info.value)


def test_extract_images_from_pdf_success():
    """Test successful image extraction from PDF."""
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Mock the fitz.open and page operations
        with patch('src.lib.pdf_parser.fitz.open') as mock_open:
            # Mock document
            mock_doc = MagicMock()
            mock_open.return_value = mock_doc

            # Mock pages
            mock_page1 = MagicMock()
            mock_page2 = MagicMock()
            mock_doc.__len__.return_value = 2
            mock_doc.load_page.side_effect = [mock_page1, mock_page2]

            # Mock image extraction
            mock_page1.get_images.return_value = [(1,)]
            mock_page2.get_images.return_value = [(2,)]
            mock_doc.extract_image.return_value = {
                "image": b"fake_image_data",
                "width": 100,
                "height": 200,
                "ext": "png"
            }

            # Mock document close
            mock_doc.close.return_value = None

            # Call the function
            result = extract_images_from_pdf(tmp_path)

            # Verify the result
            assert len(result) == 2
            assert result[0]["page"] == 1
            assert result[0]["index"] == 0
            assert result[0]["width"] == 100
            assert result[0]["height"] == 200
            assert result[0]["extension"] == "png"
            assert result[0]["data"] == b"fake_image_data"

            # Verify the mock was called correctly
            mock_open.assert_called_once_with(tmp_path)
            mock_doc.load_page.assert_any_call(0)
            mock_doc.load_page.assert_any_call(1)
            mock_page1.get_images.assert_called_once()
            mock_page2.get_images.assert_called_once()
            mock_doc.extract_image.assert_called()
            mock_doc.close.assert_called_once()

    finally:
        # Clean up temporary file
        os.unlink(tmp_path)


def test_extract_images_from_pdf_file_not_found():
    """Test image extraction with file not found."""
    with pytest.raises(FileNotFoundError):
        extract_images_from_pdf("/path/to/nonexistent.pdf")


def test_extract_images_from_pdf_general_error():
    """Test image extraction with general error."""
    with patch('src.lib.pdf_parser.fitz.open') as mock_open:
        mock_open.side_effect = Exception("Image extraction error")

        with pytest.raises(Exception) as exc_info:
            extract_images_from_pdf("/path/to/test.pdf")

        assert "Error extracting images from PDF" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])