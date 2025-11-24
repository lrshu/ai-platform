"""
Query expansion service for the RAG backend system.
"""

from src.lib.llm_client import get_llm_client
from src.lib.exceptions import QueryExpansionError
import logging

logger = logging.getLogger(__name__)


class QueryExpander:
    """Service for expanding user queries to improve search recall."""

    def __init__(self):
        """Initialize the QueryExpander."""
        self.llm_client = get_llm_client()

    def expand_query(self, query: str, num_expansions: int = 3) -> str:
        """
        Expand a query by generating related terms and phrases.

        Args:
            query: Original query to expand
            num_expansions: Number of expansions to generate

        Returns:
            Expanded query with additional terms

        Raises:
            QueryExpansionError: If query expansion fails
        """
        try:
            # Create prompt for query expansion
            prompt = f"""
            Expand the following search query by generating {num_expansions} related terms,
            synonyms, or broader concepts that might help find relevant documents.
            Return only the expanded query text, not explanations.

            Original query: {query}

            Expanded query:
            """

            # Generate expanded query using LLM
            expanded_query = self.llm_client.generate_completion(
                prompt,
                temperature=0.7,
                max_tokens=200
            )

            logger.info(f"Expanded query: {query} -> {expanded_query}")
            return expanded_query

        except Exception as e:
            logger.error(f"Failed to expand query '{query}': {e}")
            raise QueryExpansionError(f"Failed to expand query: {str(e)}")

    def expand_query_with_keywords(self, query: str) -> str:
        """
        Expand a query by extracting and adding relevant keywords.

        Args:
            query: Original query to expand

        Returns:
            Expanded query with additional keywords
        """
        try:
            # Create prompt for keyword extraction and expansion
            prompt = f"""
            Extract key terms and concepts from the following query and expand it
            with related keywords that might help find relevant documents.
            Return only the expanded query text.

            Original query: {query}

            Expanded query with keywords:
            """

            # Generate expanded query using LLM
            expanded_query = self.llm_client.generate_completion(
                prompt,
                temperature=0.5,
                max_tokens=150
            )

            logger.info(f"Expanded query with keywords: {query} -> {expanded_query}")
            return expanded_query

        except Exception as e:
            logger.error(f"Failed to expand query with keywords '{query}': {e}")
            # Return original query if expansion fails
            return query


# Global query expander instance
query_expander = QueryExpander()


def get_query_expander() -> QueryExpander:
    """
    Get the global query expander instance.

    Returns:
        QueryExpander instance
    """
    return query_expander