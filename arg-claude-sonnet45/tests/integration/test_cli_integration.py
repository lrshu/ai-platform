"""Integration tests for CLI commands with Memgraph backend."""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def test_namespace():
    """Unique namespace for test isolation."""
    return f"test-cli-{int(time.time())}"


@pytest.fixture(scope="module")
def sample_pdf():
    """Create a simple test PDF file."""
    # For now, we'll use a placeholder path
    # In production, you would create an actual PDF or use a test fixture
    test_data_dir = Path(__file__).parent.parent / "fixtures"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # Note: This is a placeholder - actual PDF creation would require pypdf or similar
    pdf_path = test_data_dir / "test_document.pdf"

    # Skip if PDF doesn't exist
    if not pdf_path.exists():
        pytest.skip("Test PDF fixture not available")

    return str(pdf_path)


@pytest.fixture(scope="module")
def cli_path():
    """Path to CLI main module."""
    return "src.cli.main"


class TestCLIIndexing:
    """Test suite for CLI indexing command."""

    def test_indexing_help(self, cli_path):
        """Test that indexing help command works."""
        result = subprocess.run(
            ["python", "-m", cli_path, "indexing", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Index a PDF document" in result.stdout
        assert "--name" in result.stdout
        assert "--file" in result.stdout

    def test_indexing_missing_required_args(self, cli_path):
        """Test indexing fails without required arguments."""
        result = subprocess.run(
            ["python", "-m", cli_path, "indexing"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_indexing_nonexistent_file(self, cli_path, test_namespace):
        """Test indexing fails with nonexistent file."""
        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "indexing",
                "--name",
                test_namespace,
                "--file",
                "/nonexistent/file.pdf",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_indexing_non_pdf_file(self, cli_path, test_namespace):
        """Test indexing fails with non-PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test content")
            temp_path = f.name

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    cli_path,
                    "indexing",
                    "--name",
                    test_namespace,
                    "--file",
                    temp_path,
                ],
                capture_output=True,
                text=True,
            )
            assert result.returncode != 0
            assert "pdf" in result.stderr.lower()
        finally:
            os.unlink(temp_path)

    @pytest.mark.skipif(
        os.getenv("QWEN_API_KEY") is None,
        reason="QWEN_API_KEY not set"
    )
    def test_indexing_success_json_output(self, cli_path, test_namespace, sample_pdf):
        """Test successful indexing with JSON output."""
        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "indexing",
                "--name",
                test_namespace,
                "--file",
                sample_pdf,
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)

        assert result.returncode == 0

        # Parse JSON output
        output = json.loads(result.stdout)
        assert output["status"] == "success"
        assert "document_id" in output
        assert "filename" in output
        assert "duration_seconds" in output

    @pytest.mark.skipif(
        os.getenv("QWEN_API_KEY") is None,
        reason="QWEN_API_KEY not set"
    )
    def test_indexing_with_custom_chunk_size(self, cli_path, test_namespace, sample_pdf):
        """Test indexing with custom chunk size."""
        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "indexing",
                "--name",
                f"{test_namespace}-custom",
                "--file",
                sample_pdf,
                "--chunk-size",
                "256",
                "--chunk-overlap",
                "25",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["status"] == "success"


class TestCLISearch:
    """Test suite for CLI search command."""

    def test_search_help(self, cli_path):
        """Test that search help command works."""
        result = subprocess.run(
            ["python", "-m", cli_path, "search", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Search indexed documents" in result.stdout
        assert "--question" in result.stdout
        assert "--top-k" in result.stdout

    def test_search_missing_required_args(self, cli_path):
        """Test search fails without required arguments."""
        result = subprocess.run(
            ["python", "-m", cli_path, "search", "--name", "test"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_search_nonexistent_namespace(self, cli_path):
        """Test search fails with nonexistent namespace."""
        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "search",
                "--name",
                "nonexistent-namespace-12345",
                "--question",
                "test query",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    @pytest.mark.skipif(
        os.getenv("QWEN_API_KEY") is None,
        reason="QWEN_API_KEY not set"
    )
    def test_search_after_indexing(self, cli_path, test_namespace):
        """Test search returns results after indexing."""
        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "search",
                "--name",
                test_namespace,
                "--question",
                "What is the main topic?",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)

        assert result.returncode == 0

        # Parse JSON output
        output = json.loads(result.stdout)
        assert output["status"] == "success"
        assert "results" in output
        assert "count" in output
        assert isinstance(output["results"], list)

    @pytest.mark.skipif(
        os.getenv("QWEN_API_KEY") is None,
        reason="QWEN_API_KEY not set"
    )
    def test_search_with_options(self, cli_path, test_namespace):
        """Test search with various options."""
        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "search",
                "--name",
                test_namespace,
                "--question",
                "test query",
                "--top-k",
                "10",
                "--expand-query",
                "--vector-only",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["status"] == "success"
        assert len(output["results"]) <= 10


class TestCLIChat:
    """Test suite for CLI chat command."""

    def test_chat_help(self, cli_path):
        """Test that chat help command works."""
        result = subprocess.run(
            ["python", "-m", cli_path, "chat", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Interactive chat" in result.stdout
        assert "--name" in result.stdout

    def test_chat_missing_required_args(self, cli_path):
        """Test chat fails without required arguments."""
        result = subprocess.run(
            ["python", "-m", cli_path, "chat"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    @pytest.mark.skipif(
        os.getenv("QWEN_API_KEY") is None,
        reason="QWEN_API_KEY not set"
    )
    def test_chat_single_interaction(self, cli_path, test_namespace):
        """Test chat with single question and exit."""
        # Send input: question + exit command
        input_text = "What is the main topic?\nexit\n"

        result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "chat",
                "--name",
                test_namespace,
            ],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Chat returns 0 on normal exit
        assert result.returncode in [0, 2]  # 0 for exit, 2 for Ctrl+C
        assert "Assistant:" in result.stdout or "RAG Chat" in result.stdout


class TestCLIGlobalOptions:
    """Test suite for global CLI options."""

    def test_help_command(self, cli_path):
        """Test main help command."""
        result = subprocess.run(
            ["python", "-m", cli_path, "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "indexing" in result.stdout
        assert "search" in result.stdout
        assert "chat" in result.stdout

    def test_verbose_flag(self, cli_path):
        """Test verbose flag enables debug logging."""
        result = subprocess.run(
            ["python", "-m", cli_path, "--verbose", "search", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_json_flag(self, cli_path):
        """Test JSON output flag."""
        # JSON flag should be respected by commands
        result = subprocess.run(
            ["python", "-m", cli_path, "--json", "search", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestCLIEndToEnd:
    """End-to-end integration tests."""

    @pytest.mark.skipif(
        os.getenv("QWEN_API_KEY") is None,
        reason="QWEN_API_KEY not set"
    )
    def test_full_pipeline(self, cli_path, sample_pdf):
        """Test complete pipeline: index -> search -> chat."""
        namespace = f"e2e-test-{int(time.time())}"

        # Step 1: Index document
        index_result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "indexing",
                "--name",
                namespace,
                "--file",
                sample_pdf,
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert index_result.returncode == 0
        index_output = json.loads(index_result.stdout)
        assert index_output["status"] == "success"
        # Verify document was indexed (document_id is present)
        assert "document_id" in index_output

        # Step 2: Search documents
        search_result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "search",
                "--name",
                namespace,
                "--question",
                "What is the content?",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert search_result.returncode == 0
        search_output = json.loads(search_result.stdout)
        assert search_output["status"] == "success"
        assert search_output["count"] > 0

        # Step 3: Chat interaction
        chat_input = "Tell me about this document.\nexit\n"
        chat_result = subprocess.run(
            [
                "python",
                "-m",
                cli_path,
                "chat",
                "--name",
                namespace,
            ],
            input=chat_input,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert chat_result.returncode in [0, 2]
        assert "Assistant:" in chat_result.stdout or "Goodbye" in chat_result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
