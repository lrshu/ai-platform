"""Search orchestrator for coordinating the search pipeline."""

import uuid
from datetime import datetime
import time
from typing import List, Dict, Any, Optional
from src.models.query import Query
from src.services.pre_retrieval.query_expander import query_expander
from src.services.retrieval.hybrid_search import hybrid_search_orchestrator
from src.services.post_retrieval.reranker import reranker
from src.lib.logging_config import logger
from src.lib.metrics import metrics_collector, TimingContext


class SearchOrchestrator:
    """Orchestrator for coordinating the search pipeline."""

    def __init__(self):
        """Initialize the search orchestrator."""
        pass

    def search(self, document_name: str, query_text: str, top_k: int = 5,
               expand_query: bool = False, rerank: bool = False) -> List[Dict[str, Any]]:
        """
        Perform a complete search through the pipeline.

        Args:
            document_name (str): Name of the document collection to search
            query_text (str): Search query
            top_k (int): Number of results to return
            expand_query (bool): Whether to expand the query
            rerank (bool): Whether to re-rank the results

        Returns:
            List[Dict[str, Any]]: Search results

        Raises:
            ValueError: If input parameters are invalid
        """
        start_time = time.time()
        context = {
            'document_name': document_name,
            'top_k': top_k,
            'expand_query': expand_query,
            'rerank': rerank
        }

        try:
            # Validate input parameters
            if not document_name or not isinstance(document_name, str):
                raise ValueError("Document name must be a non-empty string")

            if not query_text or not isinstance(query_text, str):
                raise ValueError("Query text must be a non-empty string")

            if not isinstance(top_k, int) or top_k <= 0:
                raise ValueError("top_k must be a positive integer")

            if top_k > 100:
                logger.warning(f"top_k value {top_k} is unusually high, capping at 100")
                top_k = 100

            logger.info(f"Starting search pipeline for query: {query_text}")

            # Create query object
            query = Query(
                id=str(uuid.uuid4()),
                content=query_text,
                created_at=datetime.now()
            )

            # Step 1: Query expansion (if requested)
            if expand_query:
                logger.info("Step 1: Expanding query")
                expanded_query = query_expander.expand_query(query_text)
                query.expanded_content = expanded_query
                search_query = expanded_query
                logger.info(f"Query expanded to: {expanded_query}")
            else:
                search_query = query_text

            # Step 2: Hybrid search
            logger.info("Step 2: Performing hybrid search")
            with TimingContext(metrics_collector, "hybrid_search", context):
                results = hybrid_search_orchestrator.search(document_name, search_query, top_k)

            # Step 3: Re-ranking (if requested)
            if rerank and results:
                logger.info("Step 3: Re-ranking results")
                with TimingContext(metrics_collector, "reranking", context):
                    results = reranker.rerank(query_text, results)

            logger.info(f"Search pipeline completed. Returning {len(results)} results")

            # Record overall search timing
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_timing("search_pipeline", duration_ms, context)

            return results

        except ValueError as e:
            logger.error(f"Invalid input parameters: {str(e)}")
            metrics_collector.record_counter("search_errors", 1, {"error_type": "ValueError", **context})
            raise
        except Exception as e:
            logger.error(f"Error during search pipeline: {str(e)}")
            logger.exception("Full traceback:")
            metrics_collector.record_counter("search_errors", 1, {"error_type": "Exception", **context})
            # Return empty results on error
            return []

# Global instance
search_orchestrator = SearchOrchestrator()