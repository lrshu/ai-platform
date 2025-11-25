import pytest
from unittest.mock import patch, MagicMock
from rag_backend.indexing import parse_pdf, chunk_text, get_embeddings, get_knowledge_graph, Graph

@patch('rag_backend.indexing.fitz.open')
def test_parse_pdf(mock_fitz_open):
    """
    Test parsing a PDF file by mocking the fitz.open function.
    """
    # Create a mock document object
    mock_page = MagicMock()
    mock_page.get_text.return_value = "This is a dummy PDF file for testing.\nIt contains some text about LangChain.\nLangChain is a framework for developing applications powered by language models."
    
    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [mock_page]
    
    mock_fitz_open.return_value = mock_doc

    content = parse_pdf("any/dummy/path.pdf")
    
    mock_fitz_open.assert_called_once_with("any/dummy/path.pdf")
    assert "This is a dummy PDF file for testing." in content
    assert "LangChain is a framework" in content

def test_chunk_text():
    """
    Test chunking a long text.
    """
    long_text = "This is a long text. " * 1000
    chunks = chunk_text(long_text)
    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)

@patch('rag_backend.indexing.config.DASHSCOPE_API_KEY', None)
@patch('rag_backend.indexing.DashScopeEmbeddings')
def test_get_embeddings(mock_dashscope_embeddings):
    """
    Test getting embeddings for a list of chunks.
    """
    mock_embedding_instance = MagicMock()
    mock_embedding_instance.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
    mock_dashscope_embeddings.return_value = mock_embedding_instance

    chunks = ["chunk1", "chunk2"]
    embeddings = get_embeddings(chunks)

    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.2]
    mock_dashscope_embeddings.assert_called_once_with(
        model="text-embedding-v4",
        dashscope_api_key=None
    )
    mock_embedding_instance.embed_documents.assert_called_once_with(chunks)

@patch('rag_backend.indexing.ChatPromptTemplate.from_messages')
@patch('rag_backend.indexing.ChatTongyi')
def test_get_knowledge_graph(mock_chat_tongyi, mock_from_messages):
    """
    Test getting a knowledge graph from a list of chunks.
    """
    mock_llm_instance = MagicMock()
    mock_chat_tongyi.return_value = mock_llm_instance

    mock_prompt = MagicMock()
    mock_from_messages.return_value = mock_prompt

    mock_chain = MagicMock()
    mock_prompt.__or__.return_value = mock_chain

    mock_graph = Graph(nodes=["node1", "node2"], edges=[("node1", "node2", "relationship")])
    mock_chain.invoke.return_value = mock_graph
    
    chunks = ["chunk1", "chunk2"]
    graph = get_knowledge_graph(chunks)

    assert isinstance(graph, Graph)
    assert graph.nodes == ["node1", "node2"]
    assert graph.edges == [("node1", "node2", "relationship")]
    mock_chat_tongyi.assert_called_once()
    mock_from_messages.assert_called_once()
    mock_chain.invoke.assert_called_once_with({"text": "chunk1\nchunk2"})
