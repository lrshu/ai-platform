import pytest
from typer.testing import CliRunner
from rag_backend.main import app  # Assuming your Typer app is in main.py

runner = CliRunner()

@pytest.fixture(scope="module")
def setup_knowledge_base():
    """
    Fixture to set up a knowledge base for testing.
    This will run once per test module.
    """
    # Create a dummy PDF file for testing
    with open("dummy.pdf", "w") as f:
        f.write("This is a test PDF file about LangChain.")

    result = runner.invoke(app, ["indexing", "--name", "test-kb", "--file", "dummy.pdf"])
    assert result.exit_code == 0
    assert "Successfully indexed" in result.stdout

    yield "test-kb"

    # Teardown: clean up the dummy file
    import os
    os.remove("dummy.pdf")
    # You might also want to clean up the knowledge base in the database here

def test_search(setup_knowledge_base):
    """
    Test the search functionality.
    """
    kb_name = setup_knowledge_base
    result = runner.invoke(app, ["search", "--name", kb_name, "--question", "What is this file about?"])
    assert result.exit_code == 0
    assert "LangChain" in result.stdout

def test_chat(setup_knowledge_base):
    """
    Test the chat functionality.
    """
    kb_name = setup_knowledge_base
    result = runner.invoke(app, ["chat", "--name", kb_name, "--question", "Tell me about the file."])
    assert result.exit_code == 0
    assert "LangChain" in result.stdout

def test_indexing_file_not_found():
    """
    Test that indexing fails for a non-existent file.
    """
    result = runner.invoke(app, ["indexing", "--name", "test-kb", "--file", "non_existent_file.pdf"])
    assert result.exit_code != 0
    assert "File not found" in result.stdout
