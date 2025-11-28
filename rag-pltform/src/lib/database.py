"""
Database connection module for Memgraph/Neo4j.
"""
from neo4j import GraphDatabase
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Handles connection to Memgraph/Neo4j database."""

    def __init__(self, uri: str, user: str = "", password: str = ""):
        """Initialize database connection.

        Args:
            uri: Database connection URI
            user: Database username (optional)
            password: Database password (optional)
        """
        self._uri = uri
        self._user = user
        self._password = password
        self._driver: Optional[GraphDatabase] = None

    def connect(self) -> None:
        """Establish connection to the database."""
        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password) if self._user or self._password else None
            )
            # Verify connection
            with self._driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to database at %s", self._uri)
        except Exception as e:
            logger.error("Failed to connect to database: %s", str(e))
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self._driver:
            self._driver.close()
            logger.info("Database connection closed")

    def get_driver(self):
        """Get the database driver instance."""
        if not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._driver

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()