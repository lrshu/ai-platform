"""Result re-ranking service for the search pipeline."""

from typing import List, Dict, Any
from src.lib.dashscope_client import llm_client
from src.lib.logging_config import logger, LLMError


class Reranker:
    """Service for re-ranking search results."""

    def __init__(self):
        """Initialize the re-ranker."""
        pass

    def rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-rank search results based on relevance to the query.

        Args:
            query (str): Original search query
            results (List[Dict[str, Any]]): Search results to re-rank

        Returns:
            List[Dict[str, Any]]: Re-ranked results

        Raises:
            LLMError: If there's an error with the LLM service
        """
        try:
            logger.info(f"Re-ranking {len(results)} results for query: {query}")

            # If no results, return empty list
            if not results:
                return []

            # Create a prompt for the LLM to re-rank results
            prompt = self._create_reranking_prompt(query, results)

            # Get re-ranking from LLM
            logger.info("Requesting re-ranking from LLM")
            response = llm_client.generate_completion(prompt, max_tokens=500)

            # Parse the re-ranked results
            reranked_results = self._parse_reranking_response(response, results)

            logger.info(f"Re-ranked results: {len(reranked_results)} results")
            return reranked_results

        except Exception as e:
            logger.error(f"Error re-ranking results: {str(e)}")
            raise LLMError(f"Failed to re-rank results: {str(e)}")

    def _create_reranking_prompt(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Create a prompt for the LLM to re-rank results."""
        prompt = f"Query: {query}\n\n"
        prompt += "Results to re-rank:\n"
        for i, result in enumerate(results):
            prompt += f"{i+1}. {result['content']}\n"
        prompt += "\nPlease re-rank these results based on their relevance to the query. "
        prompt += "Return only a list of numbers representing the new order (most relevant first), "
        prompt += "separated by commas. For example: 3,1,2,5,4"
        return prompt

    def _parse_reranking_response(self, response: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the LLM's re-ranking response."""
        try:
            # Extract numbers from the response
            import re
            numbers = re.findall(r'\d+', response)

            # Convert to integers and validate
            indices = [int(num) - 1 for num in numbers if 1 <= int(num) <= len(results)]

            # Remove duplicates while preserving order
            seen = set()
            unique_indices = []
            for idx in indices:
                if idx not in seen and 0 <= idx < len(results):
                    unique_indices.append(idx)
                    seen.add(idx)

            # Add any missing results at the end
            for i in range(len(results)):
                if i not in seen:
                    unique_indices.append(i)

            # Re-order results based on the new indices
            reranked_results = []
            for i, idx in enumerate(unique_indices):
                result = results[idx].copy()
                result["reranked_score"] = len(unique_indices) - i  # Higher score for better rank
                result["rank"] = i + 1
                reranked_results.append(result)

            return reranked_results

        except Exception as e:
            logger.error(f"Error parsing re-ranking response: {str(e)}")
            # Return original results with rank updated
            for i, result in enumerate(results):
                result["rank"] = i + 1
            return results


# Global instance
reranker = Reranker()