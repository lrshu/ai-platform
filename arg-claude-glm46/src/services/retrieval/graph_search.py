"""Graph search service for the search pipeline."""

from typing import List, Dict, Any
from neo4j import Transaction
from src.config.database import db_config
from src.lib.logging_config import logger, DatabaseError


class GraphSearchService:
    """Service for performing graph-based search."""

    def __init__(self):
        """Initialize the graph search service."""
        self.driver = db_config.get_driver()

    def search(self, document_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform graph-based search.

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
            logger.info(f"Performing graph search for query: {query}")

            # Search for relevant chunks based on graph relationships
            with self.driver.session() as session:
                results = session.read_transaction(
                    self._graph_search_transaction,
                    document_name,
                    query,
                    top_k
                )

            logger.info(f"Graph search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error performing graph search: {str(e)}")
            raise DatabaseError(f"Failed to perform graph search: {str(e)}")

    @staticmethod
    def _graph_search_transaction(tx: Transaction, document_name: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform graph search in a database transaction."""
        # This is a simplified implementation
        # In a real implementation, you would use more sophisticated graph queries

        # Simple keyword-based graph search
        query_words = query.lower().split()

        cypher_query = """
        MATCH (d:Document {name: $document_name})-[:CONTAINS]->(c:Chunk)
        WHERE any(word IN $query_words WHERE toLower(c.content) CONTAINS word)
        // Find related entities and their chunks
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)-[r:RELATIONSHIP]-(e2:Entity)
        OPTIONAL MATCH (e2)<-[:MENTIONS]-(c2:Chunk)
        RETURN DISTINCT c.id AS chunk_id, c.content AS content,
               count(r) + count(c2) AS graph_score
        ORDER BY graph_score DESC
        LIMIT $top_k
        """

        result = tx.run(
            cypher_query,
            document_name=document_name,
            query_words=query_words,
            top_k=top_k
        )

        return [
            {
                "chunk_id": record["chunk_id"],
                "content": record["content"],
                "score": record["graph_score"] if record["graph_score"] is not None else 0
            }
            for record in result
        ]


# Global instance
graph_search_service = GraphSearchService()