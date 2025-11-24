"""Integration tests for RAG backend system."""

import os
import sys
import uuid
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration import Orchestration

class TestRAGIntegration:
    """Integration tests for the full RAG pipeline."""

    def setup_method(self):
        """Setup test environment."""
        self.orchestration = Orchestration()
        self.test_doc_name = f"test_doc_{uuid.uuid4().hex[:8]}"
        self.test_question = "What are RAG systems?"

    def teardown_method(self):
        """Clean up after tests."""
        # In a real test, we would clean up the database
        pass

    def test_indexing_pipeline(self):
        """Test the full indexing pipeline with a mock PDF."""
        # Create a mock PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            # Write minimal PDF content (this is not a valid PDF, just for testing)
            f.write(b"%PDF-1.4\n%EOF")
            mock_pdf_path = f.name

        try:
            with patch.object(self.orchestration.indexing, 'parse_pdf') as mock_parse:
                with patch.object(self.orchestration.indexing, 'split_content') as mock_split:
                    with patch.object(self.orchestration.indexing, 'generate_embeddings') as mock_embed:
                        with patch.object(self.orchestration.indexing, 'extract_knowledge_graph') as mock_kg:
                            with patch.object(self.orchestration.indexing, 'store_content') as mock_store:
                                # Mock returns
                                mock_parse.return_value = "RAG systems retrieve relevant documents and generate answers."
                                mock_split.return_value = [
                                    {
                                        "content": "RAG systems retrieve relevant documents and generate answers.",
                                        "chunk_index": 0,
                                        "metadata": {"chunk_length": 55}
                                    }
                                ]
                                mock_embed.return_value = [
                                    {
                                        "content": "RAG systems retrieve relevant documents and generate answers.",
                                        "chunk_index": 0,
                                        "metadata": {"chunk_length": 55},
                                        "embedding": [0.1, 0.2, 0.3]
                                    }
                                ]
                                mock_kg.return_value = [
                                    {
                                        "content": "RAG systems retrieve relevant documents and generate answers.",
                                        "chunk_index": 0,
                                        "metadata": {"chunk_length": 55},
                                        "embedding": [0.1, 0.2, 0.3],
                                        "entities": ["RAG systems"],
                                        "relationships": []
                                    }
                                ]
                                mock_store.return_value = f"doc_{uuid.uuid4().hex}"

                                # Test indexing
                                result = self.orchestration.index_document(self.test_doc_name, mock_pdf_path)
                                assert result["success"] == True
                                assert "document_id" in result
                                assert result["chunk_count"] == 1

                                # Verify mock calls
                                mock_parse.assert_called_once()
                                mock_split.assert_called_once()
                                mock_embed.assert_called_once()
                                mock_kg.assert_called_once()
                                mock_store.assert_called_once()

        finally:
            os.unlink(mock_pdf_path)

    def test_search_pipeline(self):
        """Test the full search pipeline."""
        with patch.object(self.orchestration.pre_retrieval, 'pre_retrieval_process') as mock_pre:
            with patch.object(self.orchestration.retrieval, 'retrieve') as mock_retrieve:
                with patch.object(self.orchestration.post_retrieval, 'rerank') as mock_rerank:
                    # Mock returns
                    mock_pre.return_value = {
                        "original_question": self.test_question,
                        "processed_question": self.test_question,
                        "expanded_queries": [self.test_question]
                    }
                    mock_retrieve.return_value = [
                        {
                            "chunk_id": "chunk1",
                            "content": "RAG systems retrieve relevant documents and generate answers.",
                            "score": 0.9,
                            "vector_score": 0.9,
                            "graph_score": 0,
                            "match_type": ["vector"]
                        }
                    ]
                    mock_rerank.return_value = [
                        {
                            "chunk_id": "chunk1",
                            "content": "RAG systems retrieve relevant documents and generate answers.",
                            "score": 0.9,
                            "vector_score": 0.9,
                            "graph_score": 0,
                            "match_type": ["vector"],
                            "rerank_score": 0.95,
                            "final_score": 0.95
                        }
                    ]

                    # Test search
                    result = self.orchestration.retrieve_results(self.test_doc_name, self.test_question)
                    assert result["success"] == True
                    assert len(result["results"]) == 1
                    assert result["question"] == self.test_question
                    assert "expanded_queries" in result
                    assert result["results"][0]["final_score"] == 0.95

                    # Verify mock calls
                    mock_pre.assert_called_once()
                    mock_retrieve.assert_called_once()
                    mock_rerank.assert_called_once()

    def test_chat_pipeline(self):
        """Test the full chat pipeline."""
        with patch.object(self.orchestration.retrieve_results) as mock_retrieve:
            with patch.object(self.orchestration.generation, 'generate_answer') as mock_generate:
                # Mock returns
                mock_retrieve_result = {
                    "success": True,
                    "question": self.test_question,
                    "processed_question": self.test_question,
                    "expanded_queries": [self.test_question],
                    "results": [
                        {
                            "chunk_id": "chunk1",
                            "content": "RAG systems retrieve relevant documents and generate answers.",
                            "final_score": 0.95
                        }
                    ],
                    "options": {"top_k": 5, "expand_query": True, "rerank": True}
                }
                mock_retrieve.return_value = mock_retrieve_result
                mock_generate.return_value = {
                    "answer": "RAG systems retrieve relevant documents and generate answers based on that context.",
                    "sources": [
                        {
                            "chunk_id": "chunk1",
                            "content": "RAG systems retrieve relevant documents and generate answers.",
                            "score": 0.95
                        }
                    ]
                }

                # Test chat
                result = self.orchestration.generate_response(self.test_doc_name, self.test_question)
                assert result["success"] == True
                assert "answer" in result
                assert "sources" in result
                assert len(result["sources"]) == 1
                assert "RAG systems" in result["answer"]

                # Verify mock calls
                mock_retrieve.assert_called_once()
                mock_generate.assert_called_once()

if __name__ == "__main__":
    # Run tests
    import pytest
    pytest.main([__file__, "-v"])