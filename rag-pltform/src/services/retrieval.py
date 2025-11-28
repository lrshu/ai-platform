"""
Retrieval service for searching indexed documents.
"""
import logging
import time
from typing import List, Optional
from ..models.query import Query
from ..models.search_result import SearchResult
from ..models.chunk import Chunk
from ..models.vector import Vector
from ..lib.database import DatabaseConnection
from ..lib.vector_store import VectorStore
from ..lib.graph_store import GraphStore
from ..lib.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant documents based on queries."""

    def __init__(
        self,
        db_connection: DatabaseConnection,
        vector_store: Optional[VectorStore] = None,
        graph_store: Optional[GraphStore] = None
    ):
        """Initialize retrieval service.

        Args:
            db_connection: Database connection instance
            vector_store: Vector store instance (optional, will create default if not provided)
            graph_store: Graph store instance (optional, will create default if not provided)
        """
        self.db_connection = db_connection
        self.vector_store = vector_store or VectorStore(db_connection)
        self.graph_store = graph_store or GraphStore(db_connection)

    def search(
        self,
        query: Query,
        name: str,
        top_k: int = 5,
        enable_vector_search: bool = True,
        enable_graph_search: bool = True
    ) -> List[SearchResult]:
        """Search for relevant documents.

        Args:
            query: Query object
            name: Name of the document collection to search
            top_k: Number of results to return
            enable_vector_search: Enable vector similarity search
            enable_graph_search: Enable graph-based search

        Returns:
            List of SearchResult objects

        Raises:
            ValueError: If inputs are invalid
            DatabaseError: If database operations fail
        """
        logger.info("Searching for query: %s in collection: %s", query.original_text, name)
        start_time = time.time()

        # Validate inputs
        if not query or not isinstance(query, Query):
            raise ValueError("Invalid query object")

        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        if not enable_vector_search and not enable_graph_search:
            raise ValueError("At least one search method must be enabled")

        all_results = []

        # Vector search
        if enable_vector_search:
            logger.info("Performing vector search")
            vector_start = time.time()
            try:
                vector_results = self._vector_search(query, name, top_k * 2)  # Get more results for reranking
                vector_duration = time.time() - vector_start
                logger.info("Vector search completed in %.2f seconds, found %d results", vector_duration, len(vector_results))
                all_results.extend(vector_results)
            except Exception as e:
                logger.error("Vector search failed: %s", str(e))
                # Continue with other search methods if available

        # Graph search
        if enable_graph_search:
            logger.info("Performing graph search")
            graph_start = time.time()
            try:
                graph_results = self._graph_search(query, name, top_k * 2)  # Get more results for reranking
                graph_duration = time.time() - graph_start
                logger.info("Graph search completed in %.2f seconds, found %d results", graph_duration, len(graph_results))
                all_results.extend(graph_results)
            except Exception as e:
                logger.error("Graph search failed: %s", str(e))
                # Continue with other search methods if available

        # Deduplicate results by chunk_id
        unique_results = {}
        for result in all_results:
            if result.chunk_id not in unique_results:
                unique_results[result.chunk_id] = result
            else:
                # Keep the result with higher score
                if result.score > unique_results[result.chunk_id].score:
                    unique_results[result.chunk_id] = result

        # Convert to list and sort by score
        results = list(unique_results.values())
        results.sort(key=lambda x: x.score, reverse=True)

        # Limit to top_k results
        results = results[:top_k]

        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        total_duration = time.time() - start_time
        logger.info("Search completed in %.2f seconds, returning %d results", total_duration, len(results))

        return results

    def _vector_search(self, query: Query, name: str, limit: int) -> List[SearchResult]:
        """Perform vector similarity search.

        Args:
            query: Query object
            name: Name of the document collection
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects

        Raises:
            ValueError: If inputs are invalid
            DatabaseError: If database operations fail
        """
        # Validate inputs
        if not query or not isinstance(query, Query):
            raise ValueError("Invalid query object")

        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")

        if limit <= 0:
            raise ValueError("Limit must be positive")
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                # Generate query embedding
                from ..lib.llm_client import QwenClient
                llm_client = QwenClient()
                query_embedding = llm_client.generate_embedding(query.expanded_text)

                # Find relevant document IDs for the collection
                doc_query = """
                MATCH (d:Document {name: $name})
                RETURN d.id AS document_id
                """
                doc_result = session.run(doc_query, {"name": name})
                document_ids = [record["document_id"] for record in doc_result]

                if not document_ids:
                    logger.warning("No documents found for collection: %s", name)
                    return []

                # Perform vector similarity search
                vector_query = """
                MATCH (v:Vector)-[:BELONGS_TO]->(c:Chunk)-[:PART_OF]->(d:Document)
                WHERE d.id IN $document_ids
                WITH v, c, gds.alpha.similarity.cosine($query_embedding, v.embedding) AS similarity
                WHERE similarity > 0.1
                RETURN c.id AS chunk_id, similarity AS score
                ORDER BY similarity DESC
                LIMIT $limit
                """

                vector_result = session.run(vector_query, {
                    "document_ids": document_ids,
                    "query_embedding": query_embedding,
                    "limit": limit
                })

                results = []
                for i, record in enumerate(vector_result):
                    result = SearchResult(
                        query_id=query.id,
                        chunk_id=record["chunk_id"],
                        score=record["score"],
                        rank=i + 1,
                        retrieval_method="vector"
                    )
                    results.append(result)

                return results

        except Exception as e:
            logger.error("Vector search failed: %s", str(e))
            raise DatabaseError(f"Vector search failed: {str(e)}")

    def _graph_search(self, query: Query, name: str, limit: int) -> List[SearchResult]:
        """Perform graph-based search.

        Args:
            query: Query object
            name: Name of the document collection
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects

        Raises:
            ValueError: If inputs are invalid
            DatabaseError: If database operations fail
        """
        # Validate inputs
        if not query or not isinstance(query, Query):
            raise ValueError("Invalid query object")

        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")

        if limit <= 0:
            raise ValueError("Limit must be positive")
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                # Extract keywords from query
                from ..services.pre_retrieval import PreRetrievalService
                pre_service = PreRetrievalService()
                keywords = pre_service.extract_keywords(query.expanded_text)

                if not keywords:
                    logger.warning("No keywords extracted from query: %s", query.expanded_text)
                    return []

                # Find relevant document IDs for the collection
                doc_query = """
                MATCH (d:Document {name: $name})
                RETURN d.id AS document_id
                """
                doc_result = session.run(doc_query, {"name": name})
                document_ids = [record["document_id"] for record in doc_result]

                if not document_ids:
                    logger.warning("No documents found for collection: %s", name)
                    return []

                # Search for entities matching keywords
                entity_query = """
                MATCH (e:Entity)-[:MENTIONED_IN]->(c:Chunk)-[:PART_OF]->(d:Document)
                WHERE d.id IN $document_ids AND e.name IN $keywords
                RETURN c.id AS chunk_id, count(e) AS relevance_count
                ORDER BY relevance_count DESC
                LIMIT $limit
                """

                entity_result = session.run(entity_query, {
                    "document_ids": document_ids,
                    "keywords": keywords,
                    "limit": limit
                })

                results = []
                for i, record in enumerate(entity_result):
                    # Convert relevance count to a score between 0 and 1
                    score = min(record["relevance_count"] / 10.0, 1.0)
                    result = SearchResult(
                        query_id=query.id,
                        chunk_id=record["chunk_id"],
                        score=score,
                        rank=i + 1,
                        retrieval_method="graph"
                    )
                    results.append(result)

                return results

        except Exception as e:
            logger.error("Graph search failed: %s", str(e))
            raise DatabaseError(f"Graph search failed: {str(e)}")

    def get_chunk_content(self, chunk_id: str) -> Optional[Chunk]:
        """Retrieve chunk content by ID.

        Args:
            chunk_id: ID of the chunk to retrieve

        Returns:
            Chunk object or None if not found
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (c:Chunk {id: $chunk_id})
                RETURN c
                """
                result = session.run(query, {"chunk_id": chunk_id})
                record = result.single()

                if not record:
                    return None

                node = record["c"]
                return Chunk.from_dict(dict(node))
        except Exception as e:
            logger.error("Failed to retrieve chunk %s: %s", chunk_id, str(e))
            raise DatabaseError(f"Failed to retrieve chunk: {str(e)}")