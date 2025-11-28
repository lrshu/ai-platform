"""
Pre-retrieval service for processing queries before search.
"""
import logging
import time
import re
from typing import List, Set
from ..models.query import Query
from ..lib.exceptions import LLMError

logger = logging.getLogger(__name__)


class PreRetrievalService:
    """Service for processing queries before retrieval."""

    def __init__(self, llm_client=None):
        """Initialize pre-retrieval service.

        Args:
            llm_client: LLM client for query expansion (optional)
        """
        self.llm_client = llm_client

    def process_query(self, query_text: str, expand_query: bool = True) -> Query:
        """Process a query before retrieval.

        Args:
            query_text: Original query text
            expand_query: Whether to expand the query

        Returns:
            Processed Query object
        """
        start_time = time.time()
        logger.info("Processing query: %s", query_text)

        # Create query object
        query = Query(original_text=query_text)

        # Expand query if requested
        if expand_query:
            expand_start = time.time()
            expanded_text = self.expand_query(query_text)
            expand_duration = time.time() - expand_start
            query.expand_query(expanded_text)
            logger.info("Query expanded to: %s (took %.2f seconds)", expanded_text, expand_duration)

        total_duration = time.time() - start_time
        logger.info("Query processing completed in %.2f seconds", total_duration)

        return query

    def expand_query(self, query_text: str) -> str:
        """Expand query with synonyms and related terms.

        Args:
            query_text: Original query text

        Returns:
            Expanded query text
        """
        try:
            # If we have an LLM client, use it for intelligent expansion
            if self.llm_client:
                return self._expand_with_llm(query_text)
            else:
                # Simple rule-based expansion
                return self._expand_with_rules(query_text)
        except Exception as e:
            logger.warning("Failed to expand query with LLM, falling back to rule-based expansion: %s", str(e))
            return self._expand_with_rules(query_text)

    def _expand_with_llm(self, query_text: str) -> str:
        """Expand query using LLM.

        Args:
            query_text: Original query text

        Returns:
            Expanded query text
        """
        prompt = f"""
        Expand the following query by adding synonyms and related terms to improve search recall.
        Keep the original meaning intact and add relevant terms that might help find related content.

        Query: {query_text}

        Expanded query:
        """

        try:
            expanded_query = self.llm_client.generate_text(prompt, max_tokens=200, temperature=0.7)
            return expanded_query.strip()
        except LLMError:
            # Fall back to rule-based expansion
            return self._expand_with_rules(query_text)

    def _expand_with_rules(self, query_text: str) -> str:
        """Expand query using simple rules.

        Args:
            query_text: Original query text

        Returns:
            Expanded query text
        """
        # Simple synonym mapping (this would be more sophisticated in a real implementation)
        synonyms = {
            "fast": ["quick", "rapid", "speedy"],
            "slow": ["gradual", "delayed"],
            "big": ["large", "huge", "massive"],
            "small": ["tiny", "little"],
            "good": ["excellent", "great", "fine"],
            "bad": ["poor", "terrible"],
            "important": ["crucial", "significant", "essential"],
            "help": ["assist", "support"],
            "find": ["locate", "discover"],
            "create": ["make", "build", "generate"],
            "delete": ["remove", "erase"],
            "update": ["modify", "change"],
            "problem": ["issue", "difficulty", "challenge"],
            "solution": ["answer", "resolution"],
        }

        # Split query into words
        words = query_text.lower().split()
        expanded_words = set(words)  # Use set to avoid duplicates

        # Add synonyms
        for word in words:
            if word in synonyms:
                expanded_words.update(synonyms[word])

        # Join words back together
        expanded_query = " ".join(sorted(expanded_words))

        # If no expansion happened, just return the original query
        if expanded_query == query_text.lower():
            return query_text

        logger.debug("Rule-based expansion: %s -> %s", query_text, expanded_query)
        return expanded_query

    def extract_keywords(self, query_text: str) -> List[str]:
        """Extract keywords from query.

        Args:
            query_text: Query text

        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can"
        }

        # Extract words, removing punctuation
        words = re.findall(r'\b[a-zA-Z]+\b', query_text.lower())

        # Filter out stop words
        keywords = [word for word in words if word not in stop_words]

        return keywords