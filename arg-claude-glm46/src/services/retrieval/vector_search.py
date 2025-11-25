"""Vector search service for the search pipeline."""

from typing import List, Dict, Any
from neo4j import Transaction
from src.config.database import db_config
from src.services.indexing.embedder import embedder
from src.lib.logging_config import logger, DatabaseError


class VectorSearchService:
    """Service for performing vector similarity search."""

    def __init__(self):
        """Initialize the vector search service."""
        self.driver = db_config.get_driver()

    def search(self, document_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.

        Args:
            document_name (str): Name of the document collection to search
            query (str): Search query
            top_k (int): Number of results to return

        Returns:
            List[Dict[str, Any]]: List of search results

        Raises:
            DatabaseError: If there's an error querying the database
        """
        try:
            logger.info(f"Performing vector search for query: {query}")

            # Generate embedding for the query
            query_embedding = embedder.generate_embeddings([query])[0]

            # Search for similar chunks in the database
            with self.driver.session() as session:
                results = session.read_transaction(
                    self._vector_search_transaction,
                    document_name,
                    query_embedding,
                    top_k
                )

            logger.info(f"Vector search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            raise DatabaseError(f"Failed to perform vector search: {str(e)}")

    @staticmethod
    def _vector_search_transaction(tx: Transaction, document_name: str, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Perform vector search in a database transaction."""
        # This is a simplified implementation
        # In a real implementation, you would use vector similarity functions provided by the database

        query = """
        MATCH (d:Document {name: $document_name})-[:CONTAINS]->(c:Chunk)
        WHERE c.embedding IS NOT NULL
        // In a real implementation, you would use vector similarity functions here
        // For example, with Neo4j with vector support:
        // WITH c, gds.similarity.cosine(c.embedding, $query_embedding) AS similarity
        // WHERE similarity > 0.5
        // RETURN c.id AS chunk_id, c.content AS content, similarity AS score
        // ORDER BY similarity DESC
        // LIMIT $top_k
        RETURN c.id AS chunk_id, c.content AS content, rand() AS score
        ORDER BY score DESC
        LIMIT $top_k
        """

        result = tx.run(
            query,
            document_name=document_name,
            query_embedding=query_embedding,
            top_k=top_k
        )

        return [
            {
                "chunk_id": record["chunk_id"],
                "content": record["content"],
                "score": record["score"]
            }
            for record in result
        ]


# Global instance
vector_search_service = VectorSearchService()