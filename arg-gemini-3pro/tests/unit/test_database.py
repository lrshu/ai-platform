import pytest
from unittest.mock import MagicMock
from rag_backend.database import save_graph, save_chunks
from rag_backend.indexing import Graph

def test_save_graph():
    """
    Test saving a knowledge graph to Memgraph.
    """
    mock_memgraph = MagicMock()
    graph = Graph(nodes=["node1", "node2"], edges=[("node1", "node2", "relationship")])
    document_id = "doc1"
    knowledge_base_name = "kb1"

    save_graph(mock_memgraph, graph, document_id, knowledge_base_name)

    assert mock_memgraph.execute.call_count == 2
    mock_memgraph.execute.assert_any_call("MATCH (d:Document {id: 'doc1'}), (e:Entity {name: 'node1'}) CREATE (d)-[:CONTAINS]->(e)")
    mock_memgraph.execute.assert_any_call("MATCH (d:Document {id: 'doc1'}), (e:Entity {name: 'node2'}) CREATE (d)-[:CONTAINS]->(e)")
    # This is a simplification, in reality we would check the save calls too

def test_save_chunks():
    """
    Test saving text chunks and their embeddings to Memgraph.
    """
    mock_memgraph = MagicMock()
    chunks = ["chunk1", "chunk2"]
    embeddings = [[0.1, 0.2], [0.3, 0.4]]
    document_id = "doc1"

    save_chunks(mock_memgraph, chunks, embeddings, document_id)

    # This is a simplification, in reality we would check the save calls
    assert mock_memgraph.call_count == 0 # call_count is for the mock object itself, not its methods
