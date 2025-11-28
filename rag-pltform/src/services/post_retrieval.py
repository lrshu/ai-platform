"""
Post-retrieval service for processing search results.
"""
import logging
import time
from typing import List
from ..models.search_result import SearchResult
from ..models.query import Query
from ..lib.exceptions import LLMError

logger = logging.getLogger(__name__)


class PostRetrievalService:
    """Service for processing search results after retrieval."""

    def __init__(self, llm_client=None):
        """Initialize post-retrieval service.

        Args:
            llm_client: LLM client for result reranking (optional)
        """
        self.llm_client = llm_client

    def process_results(
        self,
        results: List[SearchResult],
        query: Query,
        rerank: bool = True
    ) -> List[SearchResult]:
        """Process search results after retrieval.

        Args:
            results: List of SearchResult objects
            query: Query object
            rerank: Whether to rerank the results

        Returns:
            Processed list of SearchResult objects
        """
        start_time = time.time()
        logger.info("Processing %d search results for query: %s", len(results), query.original_text)

        if not results:
            logger.info("No results to process")
            return results

        # Rerank results if requested
        if rerank and self.llm_client:
            logger.info("Reranking results")
            rerank_start = time.time()
            results = self.rerank_results(results, query)
            rerank_duration = time.time() - rerank_start
            logger.info("Reranking completed in %.2f seconds", rerank_duration)

        # Sort by score
        sort_start = time.time()
        results.sort(key=lambda x: x.score, reverse=True)
        sort_duration = time.time() - sort_start
        logger.debug("Sorting completed in %.2f seconds", sort_duration)

        # Assign final ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        total_duration = time.time() - start_time
        logger.info("Results processing completed in %.2f seconds, final count: %d", total_duration, len(results))
        return results

    def rerank_results(self, results: List[SearchResult], query: Query) -> List[SearchResult]:
        """Rerank search results based on relevance to query.

        Args:
            results: List of SearchResult objects
            query: Query object

        Returns:
            Reranked list of SearchResult objects
        """
        try:
            # Use LLM client for intelligent reranking
            if self.llm_client:
                return self._rerank_with_llm(results, query)
            else:
                # Simple score normalization
                return self._normalize_scores(results)
        except Exception as e:
            logger.warning("Failed to rerank results with LLM, falling back to score normalization: %s", str(e))
            return self._normalize_scores(results)

    def _rerank_with_llm(self, results: List[SearchResult], query: Query) -> List[SearchResult]:
        """Rerank results using LLM.

        Args:
            results: List of SearchResult objects
            query: Query object

        Returns:
            Reranked list of SearchResult objects
        """
        try:
            # Extract result texts (this would normally involve getting chunk content)
            result_texts = []
            for result in results:
                result_texts.append(f"Result {result.rank}: [content would be here]")

            # Rerank using LLM client
            reranked_indices = self.llm_client.rerank(query.original_text, result_texts)

            # Apply reranking to results
            reranked_results = []
            for item in reranked_indices:
                index = item["index"]
                if 0 <= index < len(results):
                    result = results[index]
                    result.score = item["relevance_score"]
                    reranked_results.append(result)

            return reranked_results

        except LLMError as e:
            logger.warning("LLM reranking failed: %s", str(e))
            # Fall back to score normalization
            return self._normalize_scores(results)

    def _normalize_scores(self, results: List[SearchResult]) -> List[SearchResult]:
        """Normalize scores to 0-1 range.

        Args:
            results: List of SearchResult objects

        Returns:
            List of SearchResult objects with normalized scores
        """
        if not results:
            return results

        # Find min and max scores
        scores = [result.score for result in results]
        min_score = min(scores)
        max_score = max(scores)

        # Avoid division by zero
        if max_score == min_score:
            # All scores are the same, set them to 0.5
            for result in results:
                result.score = 0.5
        else:
            # Normalize to 0-1 range
            score_range = max_score - min_score
            for result in results:
                result.score = (result.score - min_score) / score_range

        return results

    def filter_results(self, results: List[SearchResult], min_score: float = 0.1) -> List[SearchResult]:
        """Filter results based on minimum score threshold.

        Args:
            results: List of SearchResult objects
            min_score: Minimum score threshold

        Returns:
            Filtered list of SearchResult objects
        """
        filtered_results = [result for result in results if result.score >= min_score]
        logger.info("Filtered results: %d -> %d (threshold: %f)", len(results), len(filtered_results), min_score)
        return filtered_results

    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on chunk_id.

        Args:
            results: List of SearchResult objects

        Returns:
            Deduplicated list of SearchResult objects
        """
        seen_chunk_ids = set()
        deduplicated_results = []

        for result in results:
            if result.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(result.chunk_id)
                deduplicated_results.append(result)

        logger.info("Deduplicated results: %d -> %d", len(results), len(deduplicated_results))
        return deduplicated_results