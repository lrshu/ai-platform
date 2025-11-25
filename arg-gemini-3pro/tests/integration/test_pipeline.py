import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from src.main import app

@patch('fitz.open')
@patch('rag_backend.indexing.chunk_text')
@patch('rag_backend.indexing.get_embeddings')
@patch('rag_backend.indexing.get_knowledge_graph')
@patch('rag_backend.database.get_memgraph')
def test_indexing_pipeline(mock_get_memgraph, mock_get_knowledge_graph, mock_get_embeddings, mock_chunk_text, mock_fitz_open):
    """
    Test the full indexing pipeline.
    """
    # Mock return values
    mock_page = MagicMock()
    mock_page.get_text.return_value = "This is a test document."
    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc
    
    mock_chunk_text.return_value = ["This is a test document."]
    mock_get_embeddings.return_value = [[0.1, 0.2]]
    mock_get_knowledge_graph.return_value = {"nodes": ["node1"], "edges": []}
    mock_memgraph_instance = MagicMock()
    mock_get_memgraph.return_value = mock_memgraph_instance

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("dummy.pdf", "w") as f:
            f.write("This is a test document.")
        
        import os
        pdf_path = os.path.abspath("dummy.pdf")

        result = runner.invoke(app, ["indexing", "--name", "test-kb", "--file", pdf_path])

        assert result.exit_code == 0
        assert "Successfully indexed file." in result.stdout
        mock_fitz_open.assert_called_once_with(pdf_path)
        mock_chunk_text.assert_called_once_with("This is a test document.")
        mock_get_embeddings.assert_called_once_with(["This is a test document."])
        mock_get_knowledge_graph.assert_called_once_with(["This is a test document."])
        mock_get_memgraph.assert_called_once()
        # Further assertions could check the calls to save_chunks and save_graph