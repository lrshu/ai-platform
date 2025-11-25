"""Hybrid search orchestrator for combining vector and graph search."""

from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.services.retrieval.vector_search import vector_search_service
from src.services.retrieval.graph_search import graph_search_service
from src.lib.logging_config import logger


class HybridSearchOrchestrator:
    """Orchestrator for combining vector and graph search results."""

    def __init__(self):
        """Initialize the hybrid search orchestrator."""
        pass

    def search(self, document_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and graph search.

        Args:
            document_name (str): Name of the document collection to search
            query (str): Search query
            top_k (int): Number of results to return

        Returns:
            List[Dict[str, Any]]: Combined search results
        """
        try:
            logger.info(f"Performing hybrid search for query: {query}")

            # Perform vector search and graph search in parallel
            vector_results = None
            graph_results = None

            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit both search tasks
                future_vector = executor.submit(vector_search_service.search, document_name, query, top_k * 2)
                future_graph = executor.submit(graph_search_service.search, document_name, query, top_k * 2)

                # Collect results as they complete
                for future in as_completed([future_vector, future_graph]):
                    try:
                        if future == future_vector:
                            vector_results = future.result()
                            logger.info(f"Vector search completed with {len(vector_results)} results")
                        else:
                            graph_results = future.result()
                            logger.info(f"Graph search completed with {len(graph_results)} results")
                    except Exception as e:
                        logger.error(f"Error in parallel search task: {str(e)}")
                        # Continue with partial results if possible

            # Ensure we have results from both searches
            if vector_results is None:
                logger.warning("Vector search failed, falling back to graph search only")
                vector_results = []

            if graph_results is None:
                logger.warning("Graph search failed, falling back to vector search only")
                graph_results = []

            # Combine and rank results
            logger.info("Combining and ranking results")
            combined_results = self._combine_results(vector_results, graph_results, top_k)

            logger.info(f"Hybrid search returned {len(combined_results)} results")
            return combined_results

        except Exception as e:
            logger.error(f"Error performing hybrid search: {str(e)}")
            # Fallback to vector search only
            logger.info("Falling back to vector search only")
            return vector_search_service.search(document_name, query, top_k)

    def _combine_results(self, vector_results: List[Dict[str, Any]], graph_results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """
        Combine and rank results from vector and graph search.

        Args:
            vector_results (List[Dict[str, Any]]): Results from vector search
            graph_results (List[Dict[str, Any]]): Results from graph search
            top_k (int): Number of results to return

        Returns:
            List[Dict[str, Any]]: Combined and ranked results
        """
        # Create a dictionary to store combined scores
        combined_scores = {}

        # Normalize and combine vector search scores
        if vector_results:
            max_vector_score = max(result["score"] for result in vector_results) if vector_results else 1
            for result in vector_results:
                chunk_id = result["chunk_id"]
                normalized_score = result["score"] / max_vector_score if max_vector_score > 0 else result["score"]
                combined_scores[chunk_id] = {
                    "content": result["content"],
                    "vector_score": normalized_score,
                    "graph_score": 0
                }

        # Normalize and combine graph search scores
        if graph_results:
            max_graph_score = max(result["score"] for result in graph_results) if graph_results else 1
            for result in graph_results:
                chunk_id = result["chunk_id"]
                normalized_score = result["score"] / max_graph_score if max_graph_score > 0 else result["score"]
                if chunk_id in combined_scores:
                    combined_scores[chunk_id]["graph_score"] = normalized_score
                else:
                    combined_scores[chunk_id] = {
                        "content": result["content"],
                        "vector_score": 0,
                        "graph_score": normalized_score
                    }

        # Calculate combined scores (simple average)
        for chunk_id, scores in combined_scores.items():
            scores["combined_score"] = (scores["vector_score"] + scores["graph_score"]) / 2

        # Sort by combined score and return top_k results
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]["combined_score"],
            reverse=True
        )[:top_k]

        # Format results
        final_results = []
        for i, (chunk_id, scores) in enumerate(sorted_results):
            final_results.append({
                "chunk_id": chunk_id,
                "content": scores["content"],
                "score": scores["combined_score"],
                "vector_score": scores["vector_score"],
                "graph_score": scores["graph_score"],
                "rank": i + 1
            })

        return final_results


# Global instance
hybrid_search_orchestrator = HybridSearchOrchestrator()