"""
Unit tests for the embedding generator service.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.embedding_generator import EmbeddingGenerator
from src.lib.exceptions import EmbeddingGenerationError
from src.models.vector_embedding import VectorEmbedding


class TestEmbeddingGenerator:
    """Test the embedding generator service."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.generator = EmbeddingGenerator()

    def test_generate_embeddings_success(self):
        """Test successful generation of embeddings."""
        chunk_ids = ["chunk_1", "chunk_2", "chunk_3"]
        texts = ["Text one", "Text two", "Text three"]
        model_name = "text-embedding-v4"

        # Mock the DashScope TextEmbedding.call method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = {
            'embeddings': [
                {'embedding': [0.1, 0.2, 0.3]},
                {'embedding': [0.4, 0.5, 0.6]},
                {'embedding': [0.7, 0.8, 0.9]}
            ]
        }

        with patch('src.services.embedding_generator.TextEmbedding.call', return_value=mock_response):
            embeddings = self.generator.generate_embeddings(chunk_ids, texts, model_name)

            # Verify the results
            assert len(embeddings) == 3
            assert all(isinstance(embedding, VectorEmbedding) for embedding in embeddings)
            assert embeddings[0].chunk_id == "chunk_1"
            assert embeddings[0].vector == [0.1, 0.2, 0.3]
            assert embeddings[0].model_name == model_name
            assert embeddings[1].chunk_id == "chunk_2"
            assert embeddings[1].vector == [0.4, 0.5, 0.6]
            assert embeddings[2].chunk_id == "chunk_3"
            assert embeddings[2].vector == [0.7, 0.8, 0.9]

    def test_generate_embeddings_mismatched_lengths(self):
        """Test embedding generation with mismatched chunk_ids and texts."""
        chunk_ids = ["chunk_1", "chunk_2"]
        texts = ["Text one"]

        with pytest.raises(ValueError):
            self.generator.generate_embeddings(chunk_ids, texts)

    def test_generate_embeddings_empty_input(self):
        """Test embedding generation with empty input."""
        chunk_ids = []
        texts = []

        embeddings = self.generator.generate_embeddings(chunk_ids, texts)

        assert embeddings == []

    def test_generate_embeddings_client_error(self):
        """Test embedding generation when client fails."""
        chunk_ids = ["chunk_1"]
        texts = ["Text one"]

        # Mock the TextEmbedding.call method to raise an exception
        with patch('src.services.embedding_generator.TextEmbedding.call', side_effect=Exception("API error")):
            with pytest.raises(EmbeddingGenerationError):
                self.generator.generate_embeddings(chunk_ids, texts)

    def test_generate_embedding_success(self):
        """Test successful generation of a single embedding."""
        chunk_id = "chunk_1"
        text = "Text one"
        model_name = "text-embedding-v4"

        # Mock the DashScope TextEmbedding.call method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = {
            'embeddings': [
                {'embedding': [0.1, 0.2, 0.3]}
            ]
        }

        with patch('src.services.embedding_generator.TextEmbedding.call', return_value=mock_response):
            embedding = self.generator.generate_embedding(chunk_id, text, model_name)

            # Verify the result
            assert isinstance(embedding, VectorEmbedding)
            assert embedding.chunk_id == chunk_id
            assert embedding.vector == [0.1, 0.2, 0.3]
            assert embedding.model_name == model_name

    def test_generate_embedding_client_error(self):
        """Test single embedding generation when client fails."""
        chunk_id = "chunk_1"
        text = "Text one"

        # Mock the TextEmbedding.call method to raise an exception
        with patch('src.services.embedding_generator.TextEmbedding.call', side_effect=Exception("API error")):
            with pytest.raises(EmbeddingGenerationError):
                self.generator.generate_embedding(chunk_id, text)


if __name__ == "__main__":
    pytest.main([__file__])