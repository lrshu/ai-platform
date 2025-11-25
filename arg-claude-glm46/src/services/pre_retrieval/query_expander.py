"""Query expansion service for the search pipeline."""

import re
from typing import List
from src.lib.logging_config import logger


class QueryExpander:
    """Service for expanding user queries to improve retrieval effectiveness."""

    def __init__(self):
        """Initialize the query expander."""
        # In a real implementation, this might load synonyms, word embeddings, or other resources
        # For now, we'll use a simple placeholder implementation
        pass

    def expand_query(self, query: str) -> str:
        """
        Expand a query by adding synonyms and related terms.

        Args:
            query (str): Original query

        Returns:
            str: Expanded query
        """
        try:
            logger.info(f"Expanding query: {query}")

            # Simple expansion logic (this is just a placeholder)
            # In a real implementation, you would use NLP techniques, word embeddings, etc.

            # Add some common question words if they're not already present
            expanded_terms = []

            # Split query into words
            words = query.lower().split()

            # Add synonyms for common words (this is a very simple example)
            synonym_map = {
                "what": ["what", "which", "how"],
                "how": ["what", "which", "how"],
                "why": ["what", "which", "how", "reason"],
                "when": ["what", "which", "how", "time"],
                "where": ["what", "which", "how", "location", "place"],
                "who": ["what", "which", "how", "person"],
                "find": ["search", "look", "discover", "locate"],
                "search": ["find", "look", "discover", "locate"],
                "get": ["find", "search", "obtain", "retrieve"],
                "show": ["display", "present", "reveal", "show"],
                "explain": ["describe", "detail", "elaborate", "clarify"]
            }

            # Add original words and their synonyms
            expanded_words = set(words)
            for word in words:
                if word in synonym_map:
                    expanded_words.update(synonym_map[word])

            # Create expanded query
            expanded_query = " ".join(sorted(expanded_words))

            logger.info(f"Query expanded from '{query}' to '{expanded_query}'")
            return expanded_query

        except Exception as e:
            logger.error(f"Error expanding query '{query}': {str(e)}")
            # Return original query if expansion fails
            return query


# Global instance
query_expander = QueryExpander()