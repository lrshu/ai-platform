"""
Utility functions for the RAG backend system.
"""

import os
import hashlib
from typing import List, Optional
from pathlib import Path


def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Failed to read file {file_path}: {e}")


def write_file(file_path: str, content: str) -> None:
    """
    Write content to a file.

    Args:
        file_path: Path to the file
        content: Content to write

    Raises:
        IOError: If file cannot be written
    """
    try:
        # Create parent directories if they don't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError as e:
        raise IOError(f"Failed to write file {file_path}: {e}")


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: Path to the file

    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(file_path)


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension.

    Args:
        file_path: Path to the file

    Returns:
        File extension (e.g., '.pdf', '.txt')
    """
    return Path(file_path).suffix.lower()


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    return os.path.getsize(file_path)


def generate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Generate a hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hex digest of the file hash

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm is not supported
    """
    if not file_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters for most file systems
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)

    # Limit length (most filesystems have 255 char limit)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename


def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to split
        chunk_size: Size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)

        # Move start position for next chunk
        start = end - overlap
        if start >= len(text):
            break

        # If we're at the end and there's a small remaining chunk, include it
        if start + chunk_size >= len(text) and start < len(text):
            remaining = text[start:]
            if len(remaining) > overlap:  # Only add if it's substantial
                chunks.append(remaining)
            break

    return chunks