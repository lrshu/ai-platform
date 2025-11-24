"""
Hybrid retrieval service for the RAG backend system.
"""

from typing import List, Tuple
from src.services.query_expander import get_query_expander
from src.services.vector_search import get_vector_search_service
from src.services.graph_search import get_graph_search_service
from src.lib.rerank_client import get_rerank_client
from src.models.query import Query
from src.models.retrieval_result import RetrievalResult
from src.lib.exceptions import SearchError
import logging

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for performing hybrid retrieval combining vector and graph search."""

    def __init__(self):
        """Initialize the RetrievalService."""
        self.query_expander = get_query_expander()
        self.vector_search = get_vector_search_service()
        self.graph_search = get_graph_search_service()
        self.rerank_client = get_rerank_client()

    def hybrid_search(self, query_text: str, collection_name: str, top_k: int = 5,
                     enable_query_expansion: bool = True, enable_reranking: bool = True,
                     enable_vector_search: bool = True, enable_graph_search: bool = True) -> List[RetrievalResult]:
        """
        Perform hybrid search using both vector and graph-based methods.

        Args:
            query_text: Search query text
            collection_name: Name of the document collection to search
            top_k: Number of results to return
            enable_query_expansion: Whether to expand the query
            enable_reranking: Whether to re-rank results
            enable_vector_search: Whether to perform vector search
            enable_graph_search: Whether to perform graph search

        Returns:
            List of RetrievalResult objects

        Raises:
            SearchError: If search fails
        """
        try:
            # Step 1: Expand query if enabled
            if enable_query_expansion:
                expanded_query = self.query_expander.expand_query(query_text)
                logger.info(f"Expanded query: {query_text} -> {expanded_query}")
                search_query = expanded_query
            else:
                search_query = query_text

            # Step 2: Perform vector search if enabled
            vector_results = []
            if enable_vector_search:
                vector_results = self.vector_search.search_by_vector(
                    search_query, collection_name, top_k * 2  # Get more results for reranking
                )
                logger.info(f"Vector search returned {len(vector_results)} results")

            # Step 3: Perform graph search if enabled
            graph_results = []
            if enable_graph_search:
                # Extract entities from query for graph search
                entities = self._extract_entities_from_query(search_query)
                if entities:
                    graph_results = self.graph_search.search_by_entities(
                        entities, collection_name, top_k * 2
                    )
                    logger.info(f"Graph search returned {len(graph_results)} results")

            # Step 4: Combine results
            combined_results = self._combine_results(vector_results, graph_results, top_k * 2)

            # Step 5: Re-rank results if enabled
            if enable_reranking and combined_results:
                reranked_results = self._rerank_results(search_query, combined_results, top_k)
                logger.info(f"Re-ranked results from {len(combined_results)} to {len(reranked_results)}")
                final_results = reranked_results
            else:
                # Just take top_k results
                final_results = combined_results[:top_k]

            # Step 6: Convert to RetrievalResult objects
            query_obj = Query(content=query_text)
            retrieval_results = []
            for i, (chunk_id, score) in enumerate(final_results):
                result = RetrievalResult(
                    query_id=query_obj.id,
                    chunk_id=chunk_id,
                    relevance_score=score,
                    rank=i + 1
                )
                retrieval_results.append(result)

            logger.info(f"Hybrid search completed with {len(retrieval_results)} results")
            return retrieval_results

        except Exception as e:
            logger.error(f"Hybrid search failed for query '{query_text}': {e}")
            raise SearchError(f"Hybrid search failed: {str(e)}")

    def _extract_entities_from_query(self, query: str) -> List[str]:
        """
        Extract potential entities from a query.

        Args:
            query: Query text

        Returns:
            List of potential entity names
        """
        # Simple entity extraction - in real implementation would use NER
        # For now, just split by common delimiters and filter
        import re
        words = re.findall(r'\b[A-Z][a-z]*\b', query)
        return words[:10]  # Limit to first 10 potential entities

    def _combine_results(self, vector_results: List[Tuple[str, float]],
                        graph_results: List[Tuple[str, float]], max_results: int) -> List[Tuple[str, float]]:
        """
        Combine vector and graph search results.

        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            max_results: Maximum number of results to return

        Returns:
            Combined results sorted by score
        """
        # Create a dictionary to store chunk_id -> max_score
        combined_scores = {}

        # Add vector search results
        for chunk_id, score in vector_results:
            combined_scores[chunk_id] = max(combined_scores.get(chunk_id, 0), score)

        # Add graph search results (give them a boost since they're more specific)
        for chunk_id, score in graph_results:
            boosted_score = score * 1.2  # Boost graph results
            combined_scores[chunk_id] = max(combined_scores.get(chunk_id, 0), boosted_score)

        # Sort by score and limit results
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:max_results]

    def _rerank_results(self, query: str, results: List[Tuple[str, float]], top_k: int) -> List[Tuple[str, float]]:
        """
        Re-rank results using the reranking service.

        Args:
            query: Original query
            results: List of (chunk_id, score) tuples
            top_k: Number of results to return

        Returns:
            Re-ranked results
        """
        if not results:
            return []

        try:
            # Get document contents for reranking (simplified - would query DB in real implementation)
            documents = [f"Document content for chunk {chunk_id}" for chunk_id, _ in results]

            # Perform reranking
            reranked = self.rerank_client.rerank(query, documents)

            # Map back to chunk_ids and sort
            reranked_results = []
            for item in reranked:
                index = item["index"]
                chunk_id = results[index][0]
                score = item["relevance_score"]
                reranked_results.append((chunk_id, score))

            # Sort by reranked scores and limit
            reranked_results.sort(key=lambda x: x[1], reverse=True)
            return reranked_results[:top_k]

        except Exception as e:
            logger.warning(f"Reranking failed, returning original results: {e}")
            return results[:top_k]


# Global retrieval service instance
retrieval_service = RetrievalService()


def get_retrieval_service() -> RetrievalService:
    """
    Get the global retrieval service instance.

    Returns:
        RetrievalService instance
    """
    return retrieval_service