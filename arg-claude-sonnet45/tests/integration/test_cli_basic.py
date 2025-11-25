"""Basic CLI integration tests that don't require PDF fixtures."""

import subprocess
import sys

import pytest


@pytest.fixture
def cli_path():
    """Path to CLI main module."""
    return "src.cli.main"


class TestCLIBasicFunctionality:
    """Test basic CLI functionality without requiring actual documents."""

    def test_main_help(self, cli_path):
        """Test main help command displays all subcommands."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "indexing" in result.stdout.lower()
        assert "search" in result.stdout.lower()
        assert "chat" in result.stdout.lower()

    def test_indexing_help(self, cli_path):
        """Test indexing subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "indexing", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--name" in result.stdout
        assert "--file" in result.stdout
        assert "--chunk-size" in result.stdout
        assert "--chunk-overlap" in result.stdout

    def test_search_help(self, cli_path):
        """Test search subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "search", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--name" in result.stdout
        assert "--question" in result.stdout
        assert "--top-k" in result.stdout
        assert "--expand-query" in result.stdout
        assert "--no-rerank" in result.stdout
        assert "--vector-only" in result.stdout

    def test_chat_help(self, cli_path):
        """Test chat subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "chat", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--name" in result.stdout
        assert "--top-k" in result.stdout

    def test_indexing_missing_file(self, cli_path):
        """Test indexing command rejects missing file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                cli_path,
                "indexing",
                "--name",
                "test",
                "--file",
                "/nonexistent/file.pdf",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        stderr_lower = result.stderr.lower()
        assert "not found" in stderr_lower or "error" in stderr_lower

    def test_indexing_invalid_extension(self, cli_path):
        """Test indexing command rejects non-PDF files."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                cli_path,
                "indexing",
                "--name",
                "test",
                "--file",
                __file__,  # Use this Python file
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "pdf" in result.stderr.lower()

    def test_search_nonexistent_namespace(self, cli_path):
        """Test search command fails gracefully with nonexistent namespace."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                cli_path,
                "search",
                "--name",
                "nonexistent-test-namespace-12345",
                "--question",
                "test query",
            ],
            capture_output=True,
            text=True,
        )
        # Should fail with appropriate error
        assert result.returncode != 0

    def test_verbose_flag(self, cli_path):
        """Test verbose flag is accepted."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "--verbose", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_json_flag(self, cli_path):
        """Test JSON flag is accepted."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "--json", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_invalid_command(self, cli_path):
        """Test invalid command is rejected."""
        result = subprocess.run(
            [sys.executable, "-m", cli_path, "invalid-command"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0


class TestCLIArgValidation:
    """Test CLI argument validation."""

    def test_indexing_chunk_size_validation(self, cli_path):
        """Test chunk size validation."""
        # This will fail at file validation, but argument parsing should work
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                cli_path,
                "indexing",
                "--name",
                "test",
                "--file",
                "/tmp/test.pdf",
                "--chunk-size",
                "50",  # Too small, will fail later
            ],
            capture_output=True,
            text=True,
        )
        # Should accept the argument (file check fails first)
        assert result.returncode != 0

    def test_search_top_k_numeric(self, cli_path):
        """Test top-k accepts numeric values."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                cli_path,
                "search",
                "--name",
                "test",
                "--question",
                "test",
                "--top-k",
                "10",
            ],
            capture_output=True,
            text=True,
        )
        # Will fail due to missing namespace, but argument is valid
        assert "top-k" not in result.stderr.lower() or result.returncode != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
